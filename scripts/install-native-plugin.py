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

main.write_text(text, encoding="utf-8")
print(f"Plugins nativos instalados y registrados en {main}")
