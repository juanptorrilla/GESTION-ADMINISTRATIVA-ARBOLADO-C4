from pathlib import Path

android = Path("android")
main_files = list(android.rglob("MainActivity.java"))
if len(main_files) != 1:
    raise SystemExit(f"Se esperaba un MainActivity.java y se encontraron {len(main_files)}")

main = main_files[0]
for plugin_name in ("DownloadsPlugin", "PhotoPickerPlugin"):
    source = Path("native") / f"{plugin_name}.java"
    target = main.parent / f"{plugin_name}.java"
    plugin_text = source.read_text(encoding="utf-8")
    plugin_text = plugin_text.replace(
        "package ar.gob.comuna4.relevamiento;",
        "package ar.gob.comuna4.gestionarbolado;"
    )
    target.write_text(plugin_text, encoding="utf-8")

text = main.read_text(encoding="utf-8")
if "import android.os.Bundle;" not in text:
    lines = text.splitlines()
    package_index = next((i for i, line in enumerate(lines) if line.startswith("package ")), None)
    if package_index is None:
        raise SystemExit("No se encontró la declaración package en MainActivity.java")
    lines.insert(package_index + 1, "")
    lines.insert(package_index + 2, "import android.os.Bundle;")
    text = "\n".join(lines) + "\n"

class_line = "public class MainActivity extends BridgeActivity {"
if "registerPlugin(DownloadsPlugin.class)" not in text:
    if class_line not in text:
        raise SystemExit("No se encontró la clase MainActivity esperada")
    registration = """public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(DownloadsPlugin.class);
        registerPlugin(PhotoPickerPlugin.class);
        super.onCreate(savedInstanceState);
    }
"""
    text = text.replace(class_line, registration, 1)
elif "registerPlugin(PhotoPickerPlugin.class)" not in text:
    text = text.replace(
        "registerPlugin(DownloadsPlugin.class);",
        "registerPlugin(DownloadsPlugin.class);\n        registerPlugin(PhotoPickerPlugin.class);",
        1
    )

# El botón físico/gesto Atrás de Android vuelve al menú principal de la app.
back_handler = """
    @Override
    public void onBackPressed() {
        if (getBridge() != null && getBridge().getWebView() != null) {
            getBridge().getWebView().evaluateJavascript(
                "window.dispatchEvent(new Event('c4hardwareback'))", null
            );
        } else {
            super.onBackPressed();
        }
    }
"""
if "c4hardwareback" not in text:
    closing = text.rfind("}")
    if closing < 0:
        raise SystemExit("No se encontró el cierre de MainActivity")
    text = text[:closing] + back_handler + text[closing:]

main.write_text(text, encoding="utf-8")

# Ajustes de navegación de la aplicación contenedora (sin alterar la lógica del relevamiento).
html_file = Path("web/index.html")
html_text = html_file.read_text(encoding="utf-8")

html_replacements = [
    (
        ".admin-subhead{display:flex;align-items:center;gap:14px;margin-bottom:20px}",
        ".admin-subhead{display:flex;flex-direction:column;align-items:flex-start;gap:12px;margin:0 0 20px;padding:10px 0 0}"
    ),
    (
        "#adminBack{border:0;border-radius:10px;background:#245c43;color:white;padding:12px 14px;font-weight:700}",
        "#adminSubTitle{order:-1}\\n#adminBack{border:0;border-radius:10px;background:#245c43;color:white;padding:11px 18px;font-weight:800;font-size:14px;min-height:44px;box-shadow:0 2px 7px #173d2b22}"
    ),
    (
        "<header><button id=\"backToAdminMenu\" type=\"button\">← MENÚ PRINCIPAL</button><h1>Relevamiento Comuna 4</h1><p>Formulario digital para completar el PDF original</p></header>",
        "<header><h1>Relevamiento Comuna 4</h1><p>Formulario digital para completar el PDF original</p><button id=\"backToAdminMenu\" type=\"button\">← VOLVER AL MENÚ PRINCIPAL</button></header>"
    ),
    (
        "#legacyApp header{position:relative;padding-top:56px}",
        "#legacyApp header{position:sticky;top:0;z-index:5;padding:13px 14px}"
    ),
    (
        "#backToAdminMenu{position:absolute;top:10px;left:12px;border:1px solid #ffffff88;background:#ffffff18;color:#fff;border-radius:8px;padding:7px 10px;font-weight:700;font-size:12px}",
        "#backToAdminMenu{display:inline-flex;margin-top:12px;border:1px solid #ffffff88;background:#ffffff18;color:#fff;border-radius:9px;padding:10px 15px;min-height:42px;font-weight:800;font-size:13px}"
    ),
    (
        " document.getElementById('backToAdminMenu').addEventListener('click',showHome);\\n showHome();",
        " document.getElementById('backToAdminMenu').addEventListener('click',showHome);\\n // El botón físico o gesto Atrás de Android vuelve siempre al menú principal.\\n window.addEventListener('c4hardwareback',function(){showHome();});\\n showHome();"
    )
]
for old, new in html_replacements:
    if old in html_text:
        html_text = html_text.replace(old, new, 1)
    elif new not in html_text:
        raise SystemExit(f"No se encontró el fragmento esperado para aplicar navegación: {old[:90]}")

html_file.write_text(html_text, encoding="utf-8")
print("Botones de volver y navegación al menú principal configurados.")

print(f"Plugins nativos instalados y registrados en {main}")
