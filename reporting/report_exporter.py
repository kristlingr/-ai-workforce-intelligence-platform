import json
import re
from typing import Dict, Any

def convert_markdown_to_html(md_content: str) -> str:
    """
    Converts Markdown content to highly styled inline HTML paragraphs and tables.
    """
    html_lines = []
    lines = md_content.split("\n")
    
    in_table = False
    in_list = False
    in_code = False
    
    for line in lines:
        stripped = line.strip()
        
        # Code block
        if stripped.startswith("```"):
            if in_code:
                html_lines.append("</pre>")
                in_code = False
            else:
                html_lines.append("<pre style='background-color: #F8FAFC; padding: 12px; border-radius: 6px; overflow-x: auto; font-family: monospace;'>")
                in_code = True
            continue
            
        if in_code:
            html_lines.append(line)
            continue

        # Header 1
        if stripped.startswith("# "):
            html_lines.append(f"<h1 style='font-family: Arial, sans-serif; color: #1E293B; border-bottom: 2px solid #E2E8F0; padding-bottom: 8px;'>{stripped[2:]}</h1>")
            continue
            
        # Header 2
        if stripped.startswith("## "):
            html_lines.append(f"<h2 style='font-family: Arial, sans-serif; color: #0F172A; margin-top: 24px;'>{stripped[3:]}</h2>")
            continue
            
        # Header 3
        if stripped.startswith("### "):
            html_lines.append(f"<h3 style='font-family: Arial, sans-serif; color: #334155; margin-top: 18px;'>{stripped[4:]}</h3>")
            continue

        # Table block
        if stripped.startswith("|"):
            if not in_table:
                html_lines.append("<table style='width: 100%; border-collapse: collapse; margin: 16px 0; font-family: Arial, sans-serif;'>")
                in_table = True
            
            # Skip separator row (e.g. |---|---|)
            if re.match(r"^\|[\s\-\|]+$", stripped):
                continue
                
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            # Heuristic to check if first row is th
            is_first_row = html_lines[-1] == "<table style='width: 100%; border-collapse: collapse; margin: 16px 0; font-family: Arial, sans-serif;'>"
            tag = "th" if is_first_row else "td"
            style = "style='border: 1px solid #E2E8F0; padding: 10px 12px; text-align: left; background-color: #F8FAFC; font-weight: bold;'" if tag == "th" else "style='border: 1px solid #E2E8F0; padding: 10px 12px; text-align: left;'"
            
            row_html = "<tr>" + "".join(f"<{tag} {style}>{c}</{tag}>" for c in cells) + "</tr>"
            html_lines.append(row_html)
            continue
        else:
            if in_table:
                html_lines.append("</table>")
                in_table = False

        # Bullet list item
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                html_lines.append("<ul style='font-family: Arial, sans-serif; line-height: 1.6;'>")
                in_list = True
            content = stripped[2:]
            html_lines.append(f"<li style='margin-bottom: 6px;'>{content}</li>")
            continue
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False

        # Blockquote
        if stripped.startswith("> "):
            content = stripped[2:]
            html_lines.append(f"<blockquote style='border-left: 4px solid #3B82F6; background-color: #EFF6FF; padding: 12px 16px; margin: 16px 0; border-radius: 0 6px 6px 0; font-style: italic;'>{content}</blockquote>")
            continue

        # Empty line
        if not stripped:
            html_lines.append("<br/>")
            continue

        # Skip wrapping raw HTML tags or comment lines in paragraph tags
        if stripped.startswith("<") or stripped.startswith("<!--"):
            html_lines.append(line)
            continue

        # Regular paragraph
        paragraph = stripped
        paragraph = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", paragraph)
        paragraph = re.sub(r"`([^`]+)`", r"<code style='background-color: #F1F5F9; padding: 2px 6px; border-radius: 4px; font-family: monospace;'>\1</code>", paragraph)
        paragraph = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"<a href='\2' style='color: #2563EB; text-decoration: none;'>\1</a>", paragraph)
        
        html_lines.append(f"<p style='font-family: Arial, sans-serif; line-height: 1.6; color: #334155;'>{paragraph}</p>")

    if in_table:
        html_lines.append("</table>")
    if in_list:
        html_lines.append("</ul>")
    if in_code:
        html_lines.append("</pre>")
        
    return "\n".join(html_lines)


class ReportExporter:
    """
    Handles report exporting into various formats including Markdown, JSON, and HTML.
    """
    @staticmethod
    def export_to_markdown(report_content: str) -> str:
        return report_content

    @staticmethod
    def export_to_json(report_content: str, shared_state: Dict[str, Any]) -> str:
        return json.dumps({
            "report": report_content,
            "metadata": {
                "intent": shared_state.get("intent"),
                "timestamp": shared_state.get("metadata", {}).get("response_metadata", {}).get("timestamp"),
                "confidence_score": shared_state.get("metadata", {}).get("response_metadata", {}).get("confidence_score")
            }
        }, indent=2)

    @staticmethod
    def export_to_html(report_content: str, shared_state: Dict[str, Any]) -> str:
        body_html = convert_markdown_to_html(report_content)
        
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Workforce Intelligence Executive Briefing</title>
    <style>
        body {{
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            color: #334155;
            background-color: #FFFFFF;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }}
        h1, h2, h3, h4 {{
            color: #0F172A;
        }}
    </style>
</head>
<body>
    {body_html}
</body>
</html>
"""
        return full_html
