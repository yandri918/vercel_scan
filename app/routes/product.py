"""Product routes for QR code traceability."""
from flask import Blueprint, render_template, request, jsonify
import json
import base64

product_bp = Blueprint('product', __name__)


def decode_product_data(encoded_data):
    """Decode base64 encoded product data."""
    try:
        # Ensure correct padding for base64
        encoded_data = encoded_data.rstrip('=')
        padding = 4 - (len(encoded_data) % 4)
        if padding != 4:
            encoded_data += '=' * padding
            
        decoded_bytes = base64.urlsafe_b64decode(encoded_data)
        decoded_str = decoded_bytes.decode('utf-8')
        data = json.loads(decoded_str)
        
        # Log success for debugging
        print(f"[DECODE SUCCESS] Keys: {list(data.keys())}")
        return data
    except Exception as e:
        # Log error for debugging
        print(f"[DECODE ERROR] {type(e).__name__}: {str(e)}")
        print(f"[DECODE ERROR] Input length: {len(encoded_data)}")
        return None


@product_bp.route('/product/<batch_id>')
def product_passport(batch_id):
    """Display product passport page."""
    # Start with defaults
    product = {
        'batch_id': batch_id,
        'name': 'Produk AgriSensa',
        'variety': '',
        'farmer': 'Petani Indonesia',
        'location': 'Indonesia',
        'harvest_date': '',
        'weight': '1 kg',
        'emoji': '🌾',
        'price': None,
        'certifications': ['Organik', 'Fresh', 'Lokal'],
        'avg_temp': '',
        'avg_hum': '',
        'sun_hours': '',
        'milestones': []
    }
    
    # Try to decode if batch_id looks like Base64
    if len(batch_id) > 20 and not batch_id.startswith('BATCH'):
        try:
            # Simple decode without helper function
            encoded = batch_id.rstrip('=')
            padding = 4 - (len(encoded) % 4)
            if padding != 4:
                encoded += '=' * padding
            
            decoded_bytes = base64.urlsafe_b64decode(encoded)
            decoded_str = decoded_bytes.decode('utf-8')
            data = json.loads(decoded_str)
            
            # Check if minified keys exist
            if 'n' in data:
                climate = data.get('c', {})
                # Override defaults with decoded data
                product['batch_id'] = data.get('id', batch_id)
                product['name'] = data.get('n', product['name'])
                product['variety'] = data.get('v', '')
                product['farmer'] = data.get('f', product['farmer'])
                product['location'] = data.get('l', product['location'])
                product['harvest_date'] = data.get('d', '')
                product['weight'] = data.get('w', '1 kg')
                product['emoji'] = data.get('e', '🌾')
                product['avg_temp'] = climate.get('t', '')
                product['avg_hum'] = climate.get('h', '')
                product['sun_hours'] = climate.get('s', '')
                product['milestones'] = data.get('m', [])
                
                # Handle price
                if data.get('p') and data['p'] not in ['None', '']:
                    product['price'] = float(data['p'])
        except Exception as e:
            # Silently fail and use defaults
            print(f"Decode error: {e}")
            pass
    
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
