import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import random
import string

test_results = []

def generate_random_string(length=5):
    """Genera una cadena aleatoria de letras minúsculas."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def generate_pdf_report(results, filename_prefix="AgroRed_Frontend_Test_Report"):
    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    report_number = 1
    filename = os.path.join(reports_dir, f"{filename_prefix}_{report_number}.pdf")
    while os.path.exists(filename):
        report_number += 1
        filename = os.path.join(reports_dir, f"{filename_prefix}_{report_number}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("AgroRed Frontend Integration Test Report", styles['h1']))
    story.append(Paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 12))
    for result in results:
        style = styles['Normal']
        if "❌" in result or "FAILED" in result:
            story.append(Paragraph(f"<font color='red'>{result}</font>", style))
        elif "✅" in result or "PASSED" in result:
            story.append(Paragraph(f"<font color='green'>{result}</font>", style))
        else:
            story.append(Paragraph(result, style))
        story.append(Spacer(1, 6))
    try:
        doc.build(story)
        print(f"📊 PDF report generated: {filename}")
    except Exception as e:
        print(f"❌ Error generating PDF report: {e}")

def abrir_frontend(driver):
    try:
        driver.get("http://localhost:5173")
        time.sleep(2)
        test_results.append("✅ Frontend AgroRed abierto correctamente.")
    except Exception as e:
        test_results.append(f"❌ No se pudo abrir el frontend: {e}")
        raise

def click_nav_button(driver, text):
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, text))
    )
    driver.find_element(By.LINK_TEXT, text).click()
    time.sleep(2)

def cargar_catalogo(driver):
    try:
        click_nav_button(driver, "Catálogo")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "MuiCard-root"))
        )
        productos = driver.find_elements(By.CLASS_NAME, "MuiCard-root")
        assert len(productos) > 0
        test_results.append("✅ Catálogo cargado correctamente.")
    except Exception as e:
        test_results.append(f"❌ Falló la carga del catálogo: {e}")
        raise

def ir_a_login(driver):
    click_nav_button(driver, "Iniciar Sesión")

def crear_usuario(driver, full_name, email, password):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "register-form"))
        )
        form = driver.find_element(By.CLASS_NAME, "register-form")
        inputs = form.find_elements(By.CLASS_NAME, "register-input")
        inputs[0].send_keys(email)
        inputs[1].send_keys(full_name)
        inputs[2].send_keys(password)
        form.find_element(By.CLASS_NAME, "register-button").click()
        time.sleep(2)
        test_results.append("✅ Usuario registrado correctamente.")
    except Exception as e:
        test_results.append(f"❌ Falló el registro de usuario: {e}")
        raise

def iniciar_sesion(driver, email, password):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "login-form"))
        )
        form = driver.find_element(By.CLASS_NAME, "login-form")
        inputs = form.find_elements(By.CLASS_NAME, "login-input")
        inputs[0].send_keys(email)
        inputs[1].send_keys(password)
        form.find_element(By.CLASS_NAME, "login-button").click()
        time.sleep(2)
        test_results.append("✅ Inicio de sesión correcto.")
    except Exception as e:
        test_results.append(f"❌ Falló el inicio de sesión: {e}")
        raise

def ver_productos(driver):
    click_nav_button(driver, "Ver Productos")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "MuiCard-root"))
    )

def seleccionar_producto(driver, nombre=None, producto_id=None):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "MuiCard-root"))
        )
        producto = None
        if producto_id:
            links = driver.find_elements(By.CSS_SELECTOR, f'a[href*="/products/{producto_id}"]')
            if links:
                producto = links[0]
        elif nombre:
            cards = driver.find_elements(By.CLASS_NAME, "MuiCard-root")
            for card in cards:
                if nombre in card.text:
                    producto = card.find_element(By.TAG_NAME, "a")
                    break
        if producto:
            producto.click()
            time.sleep(2)
            test_results.append("✅ Producto seleccionado correctamente.")
        else:
            test_results.append("❌ No se encontró el producto para seleccionar.")
            raise Exception("Producto no encontrado")
    except Exception as e:
        test_results.append(f"❌ Falló la selección de producto: {e}")
        raise

def calificar_producto(driver, estrellas=5, comentario="prueba de comentario"):
    try:
        estrellas_elements = driver.find_elements(By.CSS_SELECTOR, 'span[class*="css-w8gd7d"]')
        for i in range(estrellas):
            estrellas_elements[i].click()
            time.sleep(0.2)
        textarea = driver.find_element(By.CSS_SELECTOR, 'textarea[placeholder*="Comparte tu experiencia"]')
        textarea.clear()
        textarea.send_keys(comentario)
        driver.find_element(By.XPATH, '//button[contains(text(),"Enviar Calificación")]').click()
        time.sleep(2)
        test_results.append("✅ Calificación enviada correctamente.")
    except Exception as e:
        test_results.append(f"❌ Falló la calificación de producto: {e}")
        raise

def actualizar_calificacion(driver):
    try:
        textarea = driver.find_element(By.CSS_SELECTOR, 'textarea[placeholder*="Comparte tu experiencia"]')
        textarea.clear()
        driver.find_element(By.XPATH, '//button[contains(text(),"Actualizar Calificación")]').click()
        time.sleep(2)
        test_results.append("✅ Calificación actualizada correctamente.")
    except Exception as e:
        test_results.append(f"❌ Falló la actualización de calificación: {e}")
        raise

def ir_a_añadir_producto(driver):
    click_nav_button(driver, "Añadir Producto")

def crear_producto(driver, nombre, precio, stock, whatsapp, categoria, descripcion):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "add-product-form"))
        )
        form = driver.find_element(By.CLASS_NAME, "add-product-form")
        form.find_element(By.NAME, "name").send_keys(nombre)
        form.find_element(By.NAME, "description").send_keys(descripcion)
        form.find_element(By.NAME, "price").send_keys(str(precio))
        form.find_element(By.NAME, "stock").send_keys(str(stock))
        form.find_element(By.NAME, "whatsapp_number").send_keys(whatsapp)
        form.find_element(By.NAME, "category").send_keys(categoria)
        form.find_element(By.CLASS_NAME, "add-product-submit-button").click()
        time.sleep(2)
        test_results.append("✅ Producto creado correctamente.")
    except Exception as e:
        test_results.append(f"❌ Falló la creación de producto: {e}")
        raise

def buscar_producto(driver, nombre):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "catalog-search-input"))
        )
        # Busca el input por la clase generada por MUI
        search_input = driver.find_element(By.CLASS_NAME, "css-1pzfmz2-MuiInputBase-input-MuiOutlinedInput-input")
        search_input.clear()
        search_input.send_keys(nombre)
        time.sleep(2)
        test_results.append("✅ Producto buscado correctamente.")
    except Exception as e:
        test_results.append(f"❌ Falló la búsqueda de producto: {e}")
        raise

def editar_producto(driver, producto_id):
    try:
        # Espera el enlace <a> con href que contiene el product_id y texto "Editar"
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f'//a[contains(@href, "/products/edit")]'))
        )
        driver.find_element(By.XPATH, f'//a[contains(@href, "/products/edit")]').click()
        time.sleep(2)
        test_results.append("✅ Navegó a editar producto correctamente.")
    except Exception as e:
        test_results.append(f"❌ Falló la navegación a editar producto: {e}")
        raise

def actualizar_descripcion_producto(driver):
    try:
        textarea = driver.find_element(By.NAME, "description")
        textarea.clear()
        driver.find_element(By.XPATH, '//button[contains(text(),"Guardar Cambios")]').click()
        time.sleep(2)
        test_results.append("✅ Descripción de producto actualizada correctamente.")
    except Exception as e:
        test_results.append(f"❌ Falló la actualización de descripción: {e}")
        raise

def eliminar_producto(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Eliminar")]'))
        )
        driver.find_element(By.XPATH, '//button[contains(text(),"Eliminar")]').click()
        time.sleep(2)
        test_results.append("✅ Producto eliminado correctamente.")
    except Exception as e:
        test_results.append(f"❌ Falló la eliminación de producto: {e}")
        raise

def cerrar_sesion(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Cerrar Sesión")]'))
        )
        driver.find_element(By.XPATH, '//button[contains(text(),"Cerrar Sesión")]').click()
        time.sleep(2)
        test_results.append("✅ Sesión cerrada correctamente.")
    except Exception as e:
        test_results.append(f"❌ Falló el cierre de sesión: {e}")
        raise

def main():
    options = Options()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    global test_results
    test_results = []
    try:
        test_email = f"{generate_random_string()}@agrored.com"
        test_password = "Testpassword123."
        test_full_name = "Usuario de Prueba"
        test_produc_name = f"{generate_random_string()} Producto Test"
        abrir_frontend(driver)
        cargar_catalogo(driver)
        ir_a_login(driver)
        crear_usuario(driver, test_full_name, test_email, test_password)
        iniciar_sesion(driver, test_email, test_password)
        cargar_catalogo(driver)
        seleccionar_producto(driver, nombre="Papa")  # Cambia el nombre según el producto que exista
        calificar_producto(driver, estrellas=5, comentario="prueba de comentario")
        actualizar_calificacion(driver)
        ir_a_añadir_producto(driver)
        crear_producto(driver, test_produc_name, 1000, 10, "0123456789", "Frutas", "descripción de prueba")
        cargar_catalogo(driver)
        buscar_producto(driver, test_produc_name)
        seleccionar_producto(driver, nombre=test_produc_name)
        editar_producto(driver, producto_id=None)  # Si tienes el _id, pásalo aquí
        actualizar_descripcion_producto(driver)
        cargar_catalogo(driver)
        buscar_producto(driver, test_produc_name)
        seleccionar_producto(driver, nombre=test_produc_name)
        eliminar_producto(driver)
        cargar_catalogo(driver)
        buscar_producto(driver, test_produc_name)
        cerrar_sesion(driver)
    except Exception as e:
        print(f"Error en el test: {e}")
        test_results.append(f"❌ TEST GENERAL FALLÓ: {e}")
    finally:
        driver.quit()
        generate_pdf_report(test_results, "AgroRed_Frontend_Test_Report")

if __name__ == "__main__":
    main()