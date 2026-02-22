import json
from datetime import date, timedelta

# Lista estándar de los 72 Nombres y sus Salmos (Fuente: Investigación Kabbalah)
NAMES_72 = [
    {"name": "והו", "letters": "Vehuaiah", "psalm": "Salmo 3:3", "kavana": "Viaje en el tiempo (Arrepentimiento)"},
    {"name": "ילי", "letters": "Jeliel", "psalm": "Salmo 22:19", "kavana": "Recuperar la chispa perdida"},
    {"name": "סיט", "letters": "Sitael", "psalm": "Salmo 91:2", "kavana": "Haciendo milagros"},
    {"name": "עלם", "letters": "Elemiah", "psalm": "Salmo 6:4", "kavana": "Eliminar pensamientos negativos"},
    {"name": "מהש", "letters": "Mahasiah", "psalm": "Salmo 34:4", "kavana": "Curación"},
    {"name": "להל", "letters": "Lelahel", "psalm": "Salmo 9:11", "kavana": "Estado de sueño"},
    {"name": "אכא", "letters": "Achaiah", "psalm": "Salmo 103:8", "kavana": "El ADN del alma"},
    {"name": "כהת", "letters": "Cahethel", "psalm": "Salmo 95:6", "kavana": "Desactiva energía negativa / Estrés"},
    {"name": "הזי", "letters": "Haziel", "psalm": "Salmo 25:6", "kavana": "Influencias angelicales"},
    {"name": "אלד", "letters": "Aladiah", "psalm": "Salmo 33:22", "kavana": "Protección contra el mal de ojo"},
    {"name": "לאו", "letters": "Laviah", "psalm": "Salmo 27:13", "kavana": "Desterrar los vestigios del mal"},
    {"name": "ההע", "letters": "Hahaiah", "psalm": "Salmo 10:1", "kavana": "Amor incondicional"},
    {"name": "יזל", "letters": "Iezalel", "psalm": "Salmo 98:4", "kavana": "Cielo en la Tierra"},
    {"name": "מבה", "letters": "Mebahel", "psalm": "Salmo 9:9", "kavana": "Adiós a las armas (Conflicto)"},
    {"name": "הרי", "letters": "Hariel", "psalm": "Salmo 94:22", "kavana": "Visión de largo alcance"},
    {"name": "הקם", "letters": "Hakamiah", "psalm": "Salmo 88:1", "kavana": "Deshacerse de la depresión"},
    {"name": "לאו", "letters": "Lauviah", "psalm": "Salmo 8:1", "kavana": "El gran escape (Ego)"},
    {"name": "כלי", "letters": "Caliel", "psalm": "Salmo 35:24", "kavana": "Fertilidad"},
    {"name": "לוו", "letters": "Leuviah", "psalm": "Salmo 40:1", "kavana": "Marcar a Dios (Comunicación)"},
    {"name": "פהל", "letters": "Pahaliah", "psalm": "Salmo 120:2", "kavana": "Victoria sobre las adicciones"},
    {"name": "נלך", "letters": "Nelchael", "psalm": "Salmo 31:14", "kavana": "Erradicar la plaga"},
    {"name": "ייי", "letters": "Yeiayel", "psalm": "Salmo 121:5", "kavana": "Detener la atracción fatal"},
    {"name": "מלה", "letters": "Melahel", "psalm": "Salmo 121:8", "kavana": "Compartir la llama"},
    {"name": "חהו", "letters": "Haheuiah", "psalm": "Salmo 33:18", "kavana": "Celos"},
    {"name": "נתה", "letters": "NithHaiah", "psalm": "Salmo 9:1", "kavana": "Hablar con la verdad"},
    {"name": "האא", "letters": "Haaiah", "psalm": "Salmo 119:145", "kavana": "Orden desde el caos"},
    {"name": "ירת", "letters": "Yerathel", "psalm": "Salmo 140:1", "kavana": "Socio silencioso"},
    {"name": "שאה", "letters": "Seheiah", "psalm": "Salmo 71:12", "kavana": "Alma gemela"},
    {"name": "ריי", "letters": "Reiyel", "psalm": "Salmo 54:4", "kavana": "Eliminar el odio"},
    {"name": "אום", "letters": "Omael", "psalm": "Salmo 71:5", "kavana": "Construir puentes"},
    {"name": "לכב", "letters": "Lecabel", "psalm": "Salmo 71:16", "kavana": "Terminar lo que empiezas"},
    {"name": "ושר", "letters": "Vasariah", "psalm": "Salmo 33:4", "kavana": "Recuerdos"},
    {"name": "יחו", "letters": "Yehuiah", "psalm": "Salmo 94:11", "kavana": "Revelar el lado oscuro"},
    {"name": "להח", "letters": "Lehahiah", "psalm": "Salmo 131:3", "kavana": "Olvidarse de sí mismo"},
    {"name": "כוק", "letters": "Chavakiah", "psalm": "Salmo 116:1", "kavana": "Energía sexual"},
    {"name": "מנד", "letters": "Menadel", "psalm": "Salmo 26:8", "kavana": "Sin miedo"},
    {"name": "אני", "letters": "Aniel", "psalm": "Salmo 80:18", "kavana": "El cuadro grande"},
    {"name": "חעם", "letters": "Haamiah", "psalm": "Salmo 91:9", "kavana": "Circuitos"},
    {"name": "רהע", "letters": "Rehael", "psalm": "Salmo 30:10", "kavana": "Diamante en bruto"},
    {"name": "ייז", "letters": "Yeiazel", "psalm": "Salmo 88:14", "kavana": "Palabras correctas"},
    {"name": "ההה", "letters": "Hahahel", "psalm": "Salmo 120:2", "kavana": "Autoestima"},
    {"name": "מיכ", "letters": "Michael", "psalm": "Salmo 121:7", "kavana": "Revelando lo oculto"},
    {"name": "וול", "letters": "Veuliah", "psalm": "Salmo 88:13", "kavana": "Desafiar la gravedad"},
    {"name": "ילה", "letters": "Yelahiah", "psalm": "Salmo 119:108", "kavana": "Endulzar el juicio"},
    {"name": "סאל", "letters": "Sealiah", "psalm": "Salmo 94:18", "kavana": "El poder de la prosperidad"},
    {"name": "ערי", "letters": "Ariel", "psalm": "Salmo 145:9", "kavana": "Certeza absoluta"},
    {"name": "עשל", "letters": "Asaliah", "psalm": "Salmo 92:5", "kavana": "Transformación global"},
    {"name": "מיה", "letters": "Mihael", "psalm": "Salmo 98:2", "kavana": "Unidad"},
    {"name": "והו", "letters": "Vehuel", "psalm": "Salmo 145:3", "kavana": "Felicidad"},
    {"name": "דני", "letters": "Daniel", "psalm": "Salmo 145:9", "kavana": "Suficiente es suficiente"},
    {"name": "החש", "letters": "Hahasiah", "psalm": "Salmo 104:31", "kavana": "Sin culpa"},
    {"name": "עמם", "letters": "Imamiah", "psalm": "Salmo 7:17", "kavana": "Pasión"},
    {"name": "ננא", "letters": "Nanael", "psalm": "Salmo 119:75", "kavana": "Sin agenda"},
    {"name": "נית", "letters": "Nithael", "psalm": "Salmo 103:19", "kavana": "La muerte de la muerte"},
    {"name": "מבה", "letters": "Mebahiah", "psalm": "Salmo 102:12", "kavana": "Pensamiento en acción"},
    {"name": "פוי", "letters": "Poiel", "psalm": "Salmo 145:14", "kavana": "Disipar la ira"},
    {"name": "נמם", "letters": "Nemamiah", "psalm": "Salmo 115:11", "kavana": "Escuchar a su alma"},
    {"name": "ייל", "letters": "Yeiayel", "psalm": "Salmo 6:3", "kavana": "Dejar ir"},
    {"name": "הרח", "letters": "Harahel", "psalm": "Salmo 113:3", "kavana": "Cordón umbilical"},
    {"name": "מזר", "letters": "Mitzrael", "psalm": "Salmo 145:17", "kavana": "Libertad"},
    {"name": "ומב", "letters": "Umabel", "psalm": "Salmo 113:2", "kavana": "Agua"},
    {"name": "יהה", "letters": "Iah-Hel", "psalm": "Salmo 119:159", "kavana": "Padres educadores"},
    {"name": "ענו", "letters": "Anauel", "psalm": "Salmo 100:2", "kavana": "Apreciación"},
    {"name": "מחי", "letters": "Mehiel", "psalm": "Salmo 33:18", "kavana": "Proyectarse favorablemente"},
    {"name": "דמב", "letters": "Damabiah", "psalm": "Salmo 90:13", "kavana": "Respeto a Dios"},
    {"name": "מנק", "letters": "Manakel", "psalm": "Salmo 38:21", "kavana": "Rendición de cuentas"},
    {"name": "איע", "letters": "Eyael", "psalm": "Salmo 37:4", "kavana": "Grandes expectativas"},
    {"name": "חבו", "letters": "Habuiah", "psalm": "Salmo 106:1", "kavana": "Contactar a los que partieron"},
    {"name": "ראה", "letters": "Rochel", "psalm": "Salmo 16:5", "kavana": "Objetos perdidos"},
    {"name": "יבמ", "letters": "Yibamiah", "psalm": "Salmo 145:17", "kavana": "Reconocer el diseño"},
    {"name": "היי", "letters": "Haiaiel", "psalm": "Salmo 109:30", "kavana": "Profecía y universos paralelos"},
    {"name": "מום", "letters": "Mumiah", "psalm": "Salmo 116:7", "kavana": "Purificación espiritual"}
]

data = {}
start_date = date(2026, 1, 1)

# Alineación: El 18 de Enero es el nombre 54 (índice 53)
# Por tanto, el 1 de Enero (17 días antes) sería índice 53 - 17 = 36 (Nombre 37)
start_idx = 36 

for i in range(365):
    curr_date = start_date + timedelta(days=i)
    idx = (start_idx + i) % 72
    entry = NAMES_72[idx]
    
    key = curr_date.strftime("%m-%d")
    data[key] = {
        "letters": entry["name"],
        "psalm_ref": entry["psalm"],
        "kavana": entry["kavana"],
        "source": "72 Names Cycle"
    }

# Overrides específicos de la imagen del usuario
data["01-18"]["psalm_ref"] = "Salmo 104:31" # User image override
data["01-18"]["kavana"] = "Medicina universal (Rejuvenecimiento)"

# Guardar
with open("d:/ShillongV3/data/kabbalah_insp.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("JSON Generado con éxito.")
