"""Product routes for QR code traceability."""
from flask import Blueprint, render_template, request, jsonify
import json
import base64

product_bp = Blueprint('product', __name__)


def decode_product_data(encoded_data):
    """Decode base64 encoded product data."""
    try:
        decoded = base64.urlsafe_b64decode(encoded_data + '==').decode('utf-8')
        return json.loads(decoded)
    except Exception:
        return None


@product_bp.route('/product/<batch_id>')
def product_passport(batch_id):
    """
    Display product passport page.
    Data can be passed via query params or encoded in batch_id.
    """
    # Try to get data from query params first
    product = {
        'batch_id': batch_id,
        'name': request.args.get('name', 'Produk AgriSensa'),
        'variety': request.args.get('variety', ''),
        'farmer': request.args.get('farmer', 'Petani Indonesia'),
        'location': request.args.get('location', 'Indonesia'),
        'harvest_date': request.args.get('harvest_date', ''),
        'weight': request.args.get('weight', ''),
        'price': request.args.get('price', type=float),
        'emoji': request.args.get('emoji', '🌾'),
        'certifications': request.args.getlist('cert') or ['Organik', 'Fresh', 'Lokal'],
        # Advanced Traceability 2.0
        'avg_temp': request.args.get('avg_temp'),
        'avg_hum': request.args.get('avg_hum'),
        'sun_hours': request.args.get('sun_hours'),
        'milestones': []
    }

    # Parse Milestones JSON if present
    milestones_json = request.args.get('milestones')
    if milestones_json:
        try:
            product['milestones'] = json.loads(milestones_json)
        except Exception:
            pass # Keep empty list if parse fails
    
    # If batch_id looks like encoded data, try to decode it
    if len(batch_id) > 20 and not batch_id.startswith('BATCH'):
        decoded = decode_product_data(batch_id)
        if decoded:
            product.update(decoded)
    
    return render_template('product_passport.html', product=product)


@product_bp.route('/api/product/generate-url', methods=['POST'])
def generate_product_url():
    """
    Generate a product passport URL for QR code.
    Expects JSON with product data.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    # Create query string from data
    params = []
    if data.get('name'):
        params.append(f"name={data['name']}")
    if data.get('variety'):
        params.append(f"variety={data['variety']}")
    if data.get('farmer'):
        params.append(f"farmer={data['farmer']}")
    if data.get('location'):
        params.append(f"location={data['location']}")
    if data.get('harvest_date'):
        params.append(f"harvest_date={data['harvest_date']}")
    if data.get('weight'):
        params.append(f"weight={data['weight']}")
    if data.get('price'):
        params.append(f"price={data['price']}")
    if data.get('emoji'):
        params.append(f"emoji={data['emoji']}")
    
    batch_id = data.get('batch_id', 'BATCH001')
    query_string = '&'.join(params)
    
    base_url = request.host_url.rstrip('/')
    url = f"{base_url}/product/{batch_id}"
    if query_string:
        url += f"?{query_string}"
    
    return jsonify({
        'success': True,
        'url': url,
        'batch_id': batch_id
    })
