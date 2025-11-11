import os
import glob
from bs4 import BeautifulSoup

def apply_neon_theme(html_content):
    """Apply neon theme to an HTML template."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Add neon classes to common elements
    for card in soup.find_all(class_='card'):
        if 'neon-card' not in card.get('class', []):
            card['class'] = card.get('class', []) + ['neon-card']
    
    for btn in soup.find_all(class_='btn'):
        if 'neon-btn' not in btn.get('class', []) and 'btn-primary' in btn.get('class', []):
            btn['class'] = btn.get('class', []) + ['neon-btn']
    
    for table in soup.find_all('table'):
        if 'table' in table.get('class', []) and 'neon-table' not in table.get('class', []):
            table['class'] = table.get('class', []) + ['neon-table']
    
    return str(soup)

def process_html_files(directory):
    """Process all HTML files in the given directory."""
    html_files = glob.glob(os.path.join(directory, '**/*.html'), recursive=True)
    
    for file_path in html_files:
        # Skip base.html as it's already processed
        if file_path.endswith('base.html'):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Only process files that extend base.html
        if "{% extends 'records/base.html' %}" in content:
            print(f"Processing {file_path}...")
            updated_content = apply_neon_theme(content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"Updated {file_path}")

if __name__ == "__main__":
    templates_dir = os.path.join(os.path.dirname(__file__), 'records/templates/records')
    process_html_files(templates_dir)
    print("Neon theme applied to all HTML files!")
