import json
import os
import sys

def generate_html(topic_name, content_data, template_path, output_path):
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Define placeholders and their replacements
    replacements = {
        '{{TOPIC_NAME}}': topic_name,
        '{{HERO_SUB}}': content_data['hero_sub'],
        '{{DEFINITION}}': content_data['definition'],
        '{{STAT_1_VAL}}': content_data['hero_stats'][0]['val'],
        '{{STAT_1_LBL}}': content_data['hero_stats'][0]['lbl'],
        '{{STAT_2_VAL}}': content_data['hero_stats'][1]['val'],
        '{{STAT_2_LBL}}': content_data['hero_stats'][1]['lbl'],
        '{{POWER_LINE}}': content_data['power_line'],
    }

    # Generate complex blocks

    # Why Cards
    why_html = ""
    for card in content_data['why_cards']:
         why_html += f"""    <div class="card">
      <span class="card-icon">{card['icon']}</span>
      <h3>{card['title']}</h3>
      <p>{card['desc']}</p>
    </div>\n"""
    replacements['<!-- WHY_CARDS_PLACEHOLDER -->'] = why_html

    # Pillars
    pillars_html = ""
    for pillar in content_data['pillars']:
        pillars_html += f'    <div class="card"><h3>{pillar["title"]}</h3><p>{pillar["desc"]}</p></div>\n'
    replacements['<!-- PILLARS_PLACEHOLDER -->'] = pillars_html

    # Case Studies
    examples_html = ""
    for ex in content_data['case_studies']:
        examples_html += f"""    <div class="example-item">
      <div class="example-header" onclick="toggleExample(this)">
        <div class="example-avatar">💬</div>
        <div>
          <div class="example-name">{ex['name']}</div>
          <div class="example-type">Case Study</div>
        </div>
        <span class="example-arrow">›</span>
      </div>
      <div class="example-body">
        <p>{ex['desc']}</p><p><strong>The Lesson:</strong> {ex['lesson']}</p>
      </div>
    </div>\n"""
    replacements['<!-- CASE_STUDIES_PLACEHOLDER -->'] = examples_html

    # Lessons
    lessons_html = ""
    for i, lesson in enumerate(content_data['lessons']):
        num = f"L{i+1:02d}"
        lessons_html += f"""    <div class="lesson">
      <span class="lesson-num">{num}</span>
      <p><strong>{lesson['title']}</strong> {lesson['desc']}</p>
    </div>\n"""
    replacements['<!-- LESSONS_PLACEHOLDER -->'] = lessons_html

    # Sources
    sources_html = ""
    for i, src in enumerate(content_data['sources']):
        sources_html += f'    <li><span class="src-num">[{i+1}]</span><span>{src}</span></li>\n'
    replacements['<!-- SOURCES_PLACEHOLDER -->'] = sources_html

    # Apply all replacements
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generator.py <input_content.json> [output_path/index.html]")
        sys.exit(1)

    content_file = sys.argv[1]
    template_file = 'template.html'

    if not os.path.exists(content_file):
        print(f"Error: {content_file} not found.")
        sys.exit(1)

    if not os.path.exists(template_file):
        print(f"Error: {template_file} not found.")
        sys.exit(1)

    with open(content_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Topic name from content or directory-friendly name
    topic_name = data.get('topic_name', 'The Science of Entering Flow')

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        folder_name = topic_name.replace(" ", "-")
        output_file = os.path.join(folder_name, 'index.html')

    generate_html(topic_name, data, template_file, output_file)
    print(f"Generated {output_file} for {topic_name}")
