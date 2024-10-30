class ProtocolPostProcessor:
    def __init__(self):
        self.section_numbers = {}
        self.current_section = None

    def post_process_html(self, html_content):
        """Post-process the generated HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove duplicate headings
        self._remove_duplicate_headings(soup)
        
        # Fix heading hierarchy and numbering
        self._fix_heading_hierarchy(soup)
        
        # Fix list numbering
        self._fix_list_numbering(soup)
        
        # Ensure consistent spacing
        self._fix_spacing(soup)
        
        # Fix table formatting
        self._fix_tables(soup)
        
        return str(soup)

    def _remove_duplicate_headings(self, soup):
        """Remove duplicate consecutive headings"""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for i in range(len(headings) - 1):
            current = headings[i]
            next_heading = headings[i + 1]
            if (current.get_text().strip() == next_heading.get_text().strip() and
                current.name == next_heading.name):
                next_heading.decompose()

    def _fix_heading_hierarchy(self, soup):
        """Fix heading hierarchy and add section numbering"""
        current_numbers = [0] * 6  # For h1-h6
        prev_level = 0
        
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            # Get heading level
            level = int(heading.name[1]) - 1  # Convert h1-h6 to 0-5
            
            # Reset lower level numbers
            for i in range(level + 1, 6):
                current_numbers[i] = 0
                
            # Increment current level
            current_numbers[level] += 1
            
            # Generate section number
            if level > 0:  # Don't number h1
                number = '.'.join(str(n) for n in current_numbers[:level + 1] if n > 0)
                heading.string = f"{number} {heading.get_text().strip()}"
            
            prev_level = level

    def _fix_list_numbering(self, soup):
        """Fix ordered list numbering"""
        for ol in soup.find_all('ol'):
            # Reset counter for each list
            for i, li in enumerate(ol.find_all('li', recursive=False), 1):
                # Remove existing numbering
                text = li.get_text()
                text = re.sub(r'^\d+\.\s*', '', text)  # Remove "1. " style numbering
                li.string = text

    def _fix_spacing(self, soup):
        """Ensure consistent spacing between elements"""
        # Add spacing after headings
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            heading['style'] = f"{heading.get('style', '')}; margin-bottom: 1em;"
            
        # Add spacing between paragraphs
        for p in soup.find_all('p'):
            p['style'] = f"{p.get('style', '')}; margin: 0.5em 0;"
            
        # Add spacing around lists
        for list_elem in soup.find_all(['ul', 'ol']):
            list_elem['style'] = f"{list_elem.get('style', '')}; margin: 1em 0;"

    def _fix_tables(self, soup):
        """Fix table formatting"""
        for table in soup.find_all('table'):
            # Add standard styling
            table['class'] = 'protocol-table'
            
            # Fix header cells
            if thead := table.find('thead'):
                for th in thead.find_all('th'):
                    th['style'] = """
                        background-color: #f2f2f2;
                        font-weight: bold;
                        text-align: center;
                        padding: 8px;
                        border: 1px solid #ddd;
                    """
            
            # Fix body cells
            if tbody := table.find('tbody'):
                for td in tbody.find_all('td'):
                    td['style'] = """
                        padding: 8px;
                        border: 1px solid #ddd;
                        vertical-align: top;
                    """

class ProtocolFormatter:
    # ... (previous ProtocolFormatter code) ...

    def format_protocol(self, sections):
        """Format complete protocol document with post-processing"""
        try:
            # Generate initial HTML
            html_content = super().format_protocol(sections)
            
            # Post-process the content
            post_processor = ProtocolPostProcessor()
            processed_html = post_processor.post_process_html(html_content)
            
            return processed_html
            
        except Exception as e:
            logger.error(f"Error formatting protocol: {str(e)}")
            raise
