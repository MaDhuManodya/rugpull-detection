import zipfile, xml.etree.ElementTree as ET
import re

def read_docx(path):
    ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read('word/document.xml')
        root = ET.fromstring(xml)
        return '\n'.join(''.join(n.text or '' for n in p.iter(f'{ns}t')).strip() for p in root.iter(f'{ns}p') if ''.join(n.text or '' for n in p.iter(f'{ns}t')).strip())
    except Exception as e:
        return f"Error reading {path}: {e}"

text3 = read_docx(r'd:\ACA\chapters\Chapter3_Research_Methodology.docx')
text4 = read_docx(r'd:\ACA\chapters\Chapter_4_System_Design_and_Implementation.docx')

with open('features_extract.md', 'w', encoding='utf-8') as f:
    f.write("# Chapter 3\n")
    for para in text3.split('\n'):
        if 'feature' in para.lower() or 'ratio' in para.lower() or 'score' in para.lower() or 'time' in para.lower():
            f.write(para + '\n')
            
    f.write("\n\n# Chapter 4\n")
    for para in text4.split('\n'):
        if 'feature' in para.lower() or 'ratio' in para.lower() or 'score' in para.lower() or 'time' in para.lower():
            f.write(para + '\n')
