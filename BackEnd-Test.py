import requests
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import random
import string

# Endpoints AgroRedDev
BASE_URL = "http://127.0.0.1:8000" # Asumiendo que el main.py de FastAPI corre en 8000
USERS_URL = f"{BASE_URL}/api/v1/users"
PRODUCTS_URL = f"{BASE_URL}/api/v1/products"
AUTH_URL = f"{BASE_URL}/api/v1/auth" # Endpoint para autenticación

test_results = []
test_users_ids = []
test_products_ids = []

def generate_random_string(length=5):
    """Genera una cadena aleatoria de letras minúsculas."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def register_user(full_name, email, password):
    """Registra un nuevo usuario en el sistema."""
    try:
        response = requests.post(USERS_URL, json={"full_name": full_name, "email": email, "password": password})
        response.raise_for_status()
        user_data = response.json()
        print(f"✅ Respuesta de registro de usuario: {user_data}") # Imprime la respuesta completa para depuración
        
        # Corrección: Obtener el ID del usuario usando '_id' en lugar de 'id'
        user_id = user_data.get("_id") 
        if user_id:
            print(f"✅ Usuario registrado: {user_data.get('email')} con ID: {user_id}")
            test_results.append(f"✅ Registro de usuario '{email}': PASSED. Esperado: Usuario creado con ID. Resultado: {user_id}")
        else:
            print(f"⚠️ Usuario registrado, pero ID no encontrado en la respuesta: {user_data.get('email')}")
            test_results.append(f"⚠️ Registro de usuario '{email}': PASSED (sin ID). Esperado: ID de usuario válido. Resultado: ID no encontrado. Respuesta completa: {user_data}")
        
        return user_id
    except requests.exceptions.RequestException as e:
        print(f"❌ Falló el registro de usuario '{email}': {e}")
        test_results.append(f"❌ Registro de usuario '{email}': FAILED - {e}. Esperado: Usuario creado con ID.")
        return None

def login_user(email, password):
    """Inicia sesión y obtiene un token de acceso."""
    try:
        response = requests.post(
            f"{AUTH_URL}/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        token_data = response.json()
        print(f"✅ Login exitoso para {email}. Token obtenido.")
        test_results.append(f"✅ Login de usuario '{email}': PASSED. Esperado: Token de acceso. Resultado: Token tipo: {token_data.get('token_type')}")
        return token_data.get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"❌ Falló el login para {email}: {e}")
        test_results.append(f"❌ Login de usuario '{email}': FAILED - {e}. Esperado: Token de acceso.")
        return None

def create_product(access_token, name, price=500, stock=500, whatsapp_number="0123456789", category="Fruta"):
    """Crea un producto asociado a un usuario autenticado."""
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.post(PRODUCTS_URL, json={
            "name": name,
            "price": price,
            "stock": stock,
            "whatsapp_number": whatsapp_number,
            "category": category
        }, headers=headers)
        response.raise_for_status()
        product_data = response.json()
        print(f"✅ Producto creado: {product_data}")
        product_id = str(product_data.get("_id"))  # Cambiado para usar "_id" en lugar de "id"
        if product_id:
            test_results.append(f"✅ Creación de producto '{name}': PASSED. Esperado: Producto creado con ID. Resultado: {product_id}")
            return product_id
        else:
            test_results.append(f"⚠️ Creación de producto '{name}': PASSED (sin ID). Esperado: ID de producto válido. Resultado: ID no encontrado. Respuesta completa: {product_data}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Falló la creación de producto: {e}")
        if e.response is not None:
            print(f"DEBUG: Respuesta de error al crear producto: {e.response.status_code} - {e.response.text}")
            test_results.append(f"❌ Creación de producto '{name}': FAILED - {e}. Detalles: {e.response.status_code} - {e.response.text}. Esperado: Producto creado con ID.")
        else:
            test_results.append(f"❌ Creación de producto '{name}': FAILED - {e}. Esperado: Producto creado con ID.")
        return None

def get_product(product_id):
    """Obtiene un producto por su ID."""
    try:
        response = requests.get(f"{PRODUCTS_URL}/{product_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

def get_products():
    """Obtiene todos los productos."""
    try:
        response = requests.get(PRODUCTS_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Falló la consulta de productos: {e}")
        test_results.append(f"❌ Consulta de productos: FAILED - {e}. Esperado: Lista de productos.")
        return []

def delete_product(access_token, product_id):
    """Elimina un producto por su ID."""
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.delete(f"{PRODUCTS_URL}/{product_id}", headers=headers)
        response.raise_for_status()
        print(f"🗑️ Producto con ID {product_id} eliminado.")
        test_results.append(f"🗑️ Eliminación de producto (ID: {product_id}): PASSED. Esperado: Código 204 No Content. Resultado: Eliminado.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Falló la eliminación de producto (ID: {product_id}): {e}")
        # Imprime el contenido de la respuesta para depuración del 405
        if e.response is not None:
            print(f"DEBUG: Respuesta de error al eliminar producto: {e.response.status_code} - {e.response.text}")
            test_results.append(f"❌ Eliminación de producto (ID: {product_id}): FAILED - {e}. Detalles: {e.response.status_code} - {e.response.text}. Esperado: Código 204 No Content.")
        else:
            test_results.append(f"❌ Eliminación de producto (ID: {product_id}): FAILED - {e}. Esperado: Código 204 No Content.")
        return False

def get_user(user_id, access_token):
    """Obtiene un usuario por su ID (requiere autenticación)."""
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(f"{USERS_URL}/{user_id}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

def delete_user(access_token, user_id):
    """Elimina un usuario por su ID (requiere autenticación de superusuario o propio usuario)."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.delete(f"{USERS_URL}/{user_id}", headers=headers)
        response.raise_for_status()
        print(f"🗑️ Usuario con ID {user_id} eliminado.")
        test_results.append(f"🗑️ Eliminación de usuario (ID: {user_id}): PASSED. Esperado: Código 204 No Content. Resultado: Eliminado.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Falló la eliminación de usuario (ID: {user_id}): {e}")
        if e.response is not None:
            print(f"DEBUG: Respuesta de error al eliminar usuario: {e.response.status_code} - {e.response.text}")
            test_results.append(f"❌ Eliminación de usuario (ID: {user_id}): FAILED - {e}. Detalles: {e.response.status_code} - {e.response.text}. Esperado: Código 204 No Content.")
        else:
            test_results.append(f"❌ Eliminación de usuario (ID: {user_id}): FAILED - {e}. Esperado: Código 204 No Content.")
        return False

def generate_pdf_report(results, filename_prefix="AgroRedDev_Backend_Test_Report"):
    """Genera un reporte PDF con los resultados de las pruebas."""
    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Generar un número de reporte único basado en la fecha y un contador
    now = datetime.now()
    date_str = now.strftime('%Y%m%d')
    counter = 1
    filename = os.path.join(reports_dir, f"{filename_prefix}_{counter}.pdf")
    while os.path.exists(filename):
        counter += 1
        filename = os.path.join(reports_dir, f"{filename_prefix}_{counter}.pdf")

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("AgroRedDev Backend Integration Test Report", styles['h1']))
    story.append(Paragraph(f"Fecha: {now.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 12))

    for result in results:
        style = styles['Normal']
        if "FAILED" in result:
            style = styles['Code'] # Usar un estilo diferente para fallos
            story.append(Paragraph(f"<font color='red'>{result}</font>", style))
        elif "PASSED" in result:
            story.append(Paragraph(f"<font color='green'>{result}</font>", style))
        else:
            story.append(Paragraph(result, style))
        story.append(Spacer(1, 6))

    try:
        doc.build(story)
        print(f"📊 Reporte PDF generado: {filename}")
        test_results.append(f"📊 Reporte PDF generado: {filename}")
    except Exception as e:
        print(f"❌ Error generando el reporte PDF: {e}")
        test_results.append(f"❌ Error generando el reporte PDF: FAILED - {e}")

def integration_test():
    """Ejecuta las pruebas de integración del backend."""
    global test_results, test_users_ids, test_products_ids
    test_results = []
    test_users_ids = []
    test_products_ids = []
    
    user_id = None
    product_id = None
    access_token = None
    test_email = f"{generate_random_string()}@agrored.com"
    test_password = "testpassword123"
    test_full_name = "Usuario de Prueba"

    try:
        # 1. Registrar un nuevo usuario
        test_results.append("--- INICIO DE PRUEBA: Registro de Usuario ---")
        user_id = register_user(test_full_name, test_email, test_password)
        assert user_id is not None, "❌ Falló el registro de usuario, user_id es None."
        test_users_ids.append(user_id)
        test_results.append("Assertion: User ID is not None: PASSED. Esperado: ID de usuario válido.")

        # 2. Iniciar sesión con el usuario creado para obtener un token
        test_results.append("\n--- INICIO DE PRUEBA: Login de Usuario ---")
        access_token = login_user(test_email, test_password)
        assert access_token is not None, "❌ Falló el login, access_token es None."
        test_results.append("Assertion: Access Token is not None: PASSED. Esperado: Token de acceso válido.")

        # 3. Crear un producto para ese usuario (requiere autenticación)
        test_results.append("\n--- INICIO DE PRUEBA: Creación de Producto ---")
        # Ahora create_product no necesita owner_id como parámetro, lo obtiene del token
        product_id = create_product(access_token, "Tomate Orgánico") 
        assert product_id is not None, "❌ Falló la creación de producto, product_id es None."
        test_products_ids.append(product_id)
        test_results.append("Assertion: Product ID is not None: PASSED. Esperado: ID de producto válido.")

        # # 4. Verificar que el producto está registrado y asociado al usuario
        # test_results.append("\n--- INICIO DE PRUEBA: Verificación de Producto ---")
        # products = get_products()
        # user_products = [p for p in products if p.get("owner_id") == user_id]
        # assert any(p["_id"] == product_id for p in user_products), "❌ El producto no fue registrado correctamente o no está asociado al usuario."
        # print("✅ Test completado: producto registrado y vinculado al usuario.")
        # test_results.append("✅ Verificación de registro y vinculación de producto: PASSED. Esperado: Producto encontrado y asociado al usuario.")

        # # 5. Intentar obtener el usuario por ID (requiere autenticación)
        # test_results.append("\n--- INICIO DE PRUEBA: Obtener Usuario por ID ---")
        # retrieved_user_data = get_user(user_id, access_token)
        # assert retrieved_user_data is not None and retrieved_user_data.get("_id") == user_id, "❌ No se pudo obtener el usuario por ID o el ID no coincide."
        # print(f"✅ Verificación: Usuario con ID {user_id} obtenido correctamente.")
        # test_results.append(f"✅ Verificación: Usuario con ID {user_id} obtenido: PASSED. Esperado: Datos del usuario con ID coincidente.")

    except AssertionError as ae:
        print(f"❌ Assertion Failed: {ae}")
        test_results.append(f"❌ ASSERTION FAILED: {ae}. Esperado: Que la condición de la aserción sea verdadera.")
    except Exception as e:
        print(f"❌ Error inesperado durante las pruebas: {e}")
        test_results.append(f"❌ UNEXPECTED ERROR: {e}. Esperado: Ejecución sin errores inesperados.")
    finally:
        test_results.append("\n--- INICIO DE PRUEBA: Limpieza de Datos ---")
        # Limpieza de datos: Eliminar productos y usuarios creados
        
        # Eliminar productos solo si se crearon
        if product_id:
            deleted_product = delete_product(access_token, product_id)
            if deleted_product:
                retrieved_product = get_product(product_id)
                assert retrieved_product is None, f"❌ El producto eliminado (ID: {product_id}) sigue presente."
                print(f"✅ Verificación: Producto con ID {product_id} eliminado y no encontrado.")
                test_results.append(f"✅ Verificación: Producto con ID {product_id} eliminado y no encontrado: PASSED. Esperado: Producto no encontrado después de la eliminación.")
            else:
                test_results.append(f"❌ Verificación: Producto con ID {product_id} NO eliminado correctamente. Esperado: Producto no encontrado después de la eliminación.")

        # # Eliminar usuarios solo si se crearon
        # if user_id:
        #     deleted_user = delete_user(access_token, user_id)
        #     if deleted_user:
        #         retrieved_user = get_user(user_id, access_token)
        #         assert retrieved_user is None, f"❌ El usuario eliminado (ID: {user_id}) sigue presente."
        #         print(f"✅ Verificación: Usuario con ID {user_id} eliminado y no encontrado.")
        #         test_results.append(f"✅ Verificación: Usuario con ID {user_id} eliminado y no encontrado: PASSED. Esperado: Usuario no encontrado después de la eliminación.")
        #     else:
        #         test_results.append(f"❌ Verificación: Usuario con ID {user_id} NO eliminado correctamente. Esperado: Usuario no encontrado después de la eliminación.")
        # Generar reporte PDF al final de las pruebas
        generate_pdf_report(test_results, filename_prefix="AgroRedDev_Backend_Test_Report")
if __name__ == "__main__":
    integration_test()
