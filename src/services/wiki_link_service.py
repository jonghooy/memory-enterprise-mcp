"""Service for handling wiki-link extraction and management."""

import re
import logging
from typing import List, Set, Dict, Tuple

logger = logging.getLogger(__name__)


class WikiLinkService:
    """Service for extracting and managing wiki-links."""

    # Pattern to match [[entity]] links
    WIKI_LINK_PATTERN = re.compile(r'\[\[([^\[\]]+)\]\]')

    # Pattern to match [[display|target]] links
    WIKI_LINK_ALIAS_PATTERN = re.compile(r'\[\[([^\[\]|]+)\|([^\[\]]+)\]\]')

    def extract_wiki_links(self, text: str) -> List[str]:
        """Extract all wiki-links from text."""
        if not text:
            return []

        links = set()

        # First, extract aliased links [[display|target]]
        aliased_matches = self.WIKI_LINK_ALIAS_PATTERN.findall(text)
        for display, target in aliased_matches:
            # Use the target (second part) as the entity
            links.add(target.strip().lower())

        # Then, extract simple links [[entity]]
        # Replace aliased links to avoid double-matching
        text_without_aliases = self.WIKI_LINK_ALIAS_PATTERN.sub('', text)
        simple_matches = self.WIKI_LINK_PATTERN.findall(text_without_aliases)

        for match in simple_matches:
            links.add(match.strip().lower())

        return sorted(list(links))

    def extract_wiki_links_with_positions(
        self,
        text: str,
    ) -> List[Dict[str, any]]:
        """Extract wiki-links with their positions in the text."""
        if not text:
            return []

        links = []

        # Extract aliased links with positions
        for match in self.WIKI_LINK_ALIAS_PATTERN.finditer(text):
            display = match.group(1)
            target = match.group(2)

            links.append({
                'entity': target.strip().lower(),
                'display': display.strip(),
                'start': match.start(),
                'end': match.end(),
                'text': match.group(0),
                'is_aliased': True,
            })

        # Extract simple links with positions
        text_without_aliases = text
        offset_adjustment = 0

        # Remove aliased links for simple matching
        for match in sorted(links, key=lambda x: x['start'], reverse=True):
            text_without_aliases = (
                text_without_aliases[:match['start']] +
                ' ' * (match['end'] - match['start']) +
                text_without_aliases[match['end']:]
            )

        for match in self.WIKI_LINK_PATTERN.finditer(text_without_aliases):
            entity = match.group(1)

            links.append({
                'entity': entity.strip().lower(),
                'display': entity.strip(),
                'start': match.start(),
                'end': match.end(),
                'text': match.group(0),
                'is_aliased': False,
            })

        # Sort by position
        links.sort(key=lambda x: x['start'])

        return links

    def replace_wiki_links(
        self,
        text: str,
        replacer_func=None,
    ) -> str:
        """Replace wiki-links in text with custom format."""
        if not text or not replacer_func:
            return text

        result = text

        # Get all links with positions
        links = self.extract_wiki_links_with_positions(text)

        # Replace from end to start to maintain positions
        for link in reversed(links):
            replacement = replacer_func(link)
            result = (
                result[:link['start']] +
                replacement +
                result[link['end']:]
            )

        return result

    def convert_to_markdown_links(
        self,
        text: str,
        url_pattern: str = "/memory/entity/{entity}",
    ) -> str:
        """Convert wiki-links to Markdown links."""

        def replacer(link):
            url = url_pattern.format(entity=link['entity'])
            return f"[{link['display']}]({url})"

        return self.replace_wiki_links(text, replacer)

    def convert_to_html_links(
        self,
        text: str,
        url_pattern: str = "/memory/entity/{entity}",
        css_class: str = "wiki-link",
    ) -> str:
        """Convert wiki-links to HTML links."""

        def replacer(link):
            url = url_pattern.format(entity=link['entity'])
            return f'<a href="{url}" class="{css_class}">{link["display"]}</a>'

        return self.replace_wiki_links(text, replacer)

    def extract_entities_from_text(
        self,
        text: str,
        include_wiki_links: bool = True,
    ) -> List[str]:
        """Extract potential entities from text."""
        entities = set()

        # Add wiki-link entities
        if include_wiki_links:
            entities.update(self.extract_wiki_links(text))

        # TODO: Add NER (Named Entity Recognition) here
        # This could use spaCy, NLTK, or other NLP libraries

        return sorted(list(entities))

    def normalize_entity(self, entity: str) -> str:
        """Normalize an entity name for consistent matching."""
        if not entity:
            return ""

        # Convert to lowercase
        normalized = entity.lower()

        # Remove extra whitespace
        normalized = ' '.join(normalized.split())

        # Remove special characters (keep alphanumeric and spaces)
        normalized = re.sub(r'[^\w\s-]', '', normalized)

        return normalized.strip()

    def is_valid_entity(self, entity: str) -> bool:
        """Check if an entity name is valid."""
        if not entity:
            return False

        normalized = self.normalize_entity(entity)

        # Check minimum length
        if len(normalized) < 2:
            return False

        # Check maximum length
        if len(normalized) > 100:
            return False

        # Check if it's not just numbers
        if normalized.isdigit():
            return False

        return True

    def get_context_around_link(
        self,
        text: str,
        link_position: int,
        context_size: int = 50,
    ) -> str:
        """Get text context around a wiki-link."""
        if not text or link_position < 0:
            return ""

        start = max(0, link_position - context_size)
        end = min(len(text), link_position + context_size)

        context = text[start:end]

        # Add ellipsis if truncated
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."

        return context