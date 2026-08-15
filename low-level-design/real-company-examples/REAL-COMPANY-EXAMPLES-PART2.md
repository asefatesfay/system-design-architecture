# Real Company LLD Examples - Part 2

Continuation of real-world low-level design examples from major tech companies.

> **📝 Language Note:** Examples use Python (most common for LLD interviews). For language-specific patterns:
> - [Language Comparison Guide](../lld-coding/multi-language/LANGUAGE-COMPARISON.md) - Python vs Go vs Java vs JavaScript
> - [Four Pillars Multi-Language](../03-oop-fundamentals/four-pillars/) - Core OOP in all 4 languages
> - [Design Patterns](../06-design-patterns/) - Strategy, Observer, Factory patterns
> - [Part 1](./REAL-COMPANY-EXAMPLES.md) - Rate Limiter, Notifications, Ride Matching

---

# 6. URL Shortener - bit.ly, TinyURL

**Used by**: bit.ly, TinyURL, goo.gl (discontinued), short.link

**Problem**: Convert long URLs to short, shareable links

**Patterns**: Factory (generate short codes), Strategy (encoding algorithms)

## Complete Implementation

```python
from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime
import hashlib
import random
import string

# ============================================
# URL SHORTENING STRATEGIES
# ============================================

class ShortCodeGenerator(ABC):
    """Abstract strategy for generating short codes"""

    @abstractmethod
    def generate(self, long_url: str, custom_code: Optional[str] = None) -> str:
        """Generate short code for URL"""
        pass

class HashBasedGenerator(ShortCodeGenerator):
    """
    Generate short code using hash
    Used by: Early URL shorteners

    Pros: Deterministic (same URL = same code)
    Cons: Collisions possible
    """

    def generate(self, long_url: str, custom_code: Optional[str] = None) -> str:
        if custom_code:
            return custom_code

        # MD5 hash of URL
        hash_digest = hashlib.md5(long_url.encode()).hexdigest()

        # Take first 7 characters
        return hash_digest[:7]

class Base62Generator(ShortCodeGenerator):
    """
    Generate short code using base62 encoding
    Used by: bit.ly, TinyURL

    Base62: [a-zA-Z0-9] = 62 characters
    7 characters = 62^7 = 3.5 trillion possible URLs

    Pros: Short codes, URL-safe characters
    Cons: Sequential (can be guessed)
    """

    def __init__(self):
        self.chars = string.ascii_letters + string.digits  # a-zA-Z0-9
        self.base = len(self.chars)  # 62
        self.counter = 1000000  # Start from 1 million

    def generate(self, long_url: str, custom_code: Optional[str] = None) -> str:
        if custom_code:
            return custom_code

        # Generate next ID
        num = self.counter
        self.counter += 1

        # Convert to base62
        return self._encode_base62(num)

    def _encode_base62(self, num: int) -> str:
        """Convert number to base62 string"""
        if num == 0:
            return self.chars[0]

        result = []
        while num > 0:
            result.append(self.chars[num % self.base])
            num //= self.base

        return ''.join(reversed(result))

class RandomGenerator(ShortCodeGenerator):
    """
    Generate random short code
    Used by: Many modern shorteners

    Pros: Unpredictable, secure
    Cons: Need to check for collisions
    """

    def __init__(self, length: int = 7):
        self.length = length
        self.chars = string.ascii_letters + string.digits

    def generate(self, long_url: str, custom_code: Optional[str] = None) -> str:
        if custom_code:
            return custom_code

        return ''.join(random.choices(self.chars, k=self.length))

# ============================================
# URL MODEL
# ============================================

class ShortenedURL:
    """Model for shortened URL"""

    def __init__(
        self,
        short_code: str,
        long_url: str,
        creator: Optional[str] = None,
        custom_alias: bool = False
    ):
        self.short_code = short_code
        self.long_url = long_url
        self.creator = creator
        self.custom_alias = custom_alias

        # Metadata
        self.created_at = datetime.now()
        self.clicks = 0
        self.last_accessed = None

        # Analytics
        self.referrers: Dict[str, int] = {}
        self.locations: Dict[str, int] = {}

    def record_click(self, referrer: str = "direct", location: str = "unknown"):
        """Record a click on this short URL"""
        self.clicks += 1
        self.last_accessed = datetime.now()

        self.referrers[referrer] = self.referrers.get(referrer, 0) + 1
        self.locations[location] = self.locations.get(location, 0) + 1

    def get_analytics(self) -> dict:
        """Get analytics for this URL"""
        return {
            'short_code': self.short_code,
            'long_url': self.long_url,
            'total_clicks': self.clicks,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'top_referrers': sorted(
                self.referrers.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            'top_locations': sorted(
                self.locations.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }

# ============================================
# URL SHORTENER SERVICE
# ============================================

class URLShortener:
    """
    Complete URL shortener like bit.ly

    Features:
    - Multiple encoding strategies
    - Custom aliases
    - Analytics
    - Collision handling
    """

    def __init__(
        self,
        domain: str = "short.link",
        generator: ShortCodeGenerator = None
    ):
        self.domain = domain
        self.generator = generator or Base62Generator()

        # Storage (in real app: database)
        self.url_map: Dict[str, ShortenedURL] = {}
        self.reverse_map: Dict[str, str] = {}

    def shorten(
        self,
        long_url: str,
        custom_alias: Optional[str] = None,
        creator: Optional[str] = None
    ) -> str:
        """Shorten a URL"""

        if not self._is_valid_url(long_url):
            raise ValueError(f"Invalid URL: {long_url}")

        if long_url in self.reverse_map:
            existing_code = self.reverse_map[long_url]
            return self._build_short_url(existing_code)

        if custom_alias:
            if not self._is_valid_alias(custom_alias):
                raise ValueError(f"Invalid alias: {custom_alias}")
            if custom_alias in self.url_map:
                raise ValueError(f"Alias '{custom_alias}' already taken")

        # Generate short code
        max_attempts = 10
        for attempt in range(max_attempts):
            short_code = self.generator.generate(long_url, custom_alias)

            if short_code not in self.url_map:
                break

            if attempt == max_attempts - 1:
                raise RuntimeError("Could not generate unique short code")

        # Store mapping
        shortened_url = ShortenedURL(
            short_code=short_code,
            long_url=long_url,
            creator=creator,
            custom_alias=bool(custom_alias)
        )

        self.url_map[short_code] = shortened_url
        self.reverse_map[long_url] = short_code

        full_short_url = self._build_short_url(short_code)
        print(f"✓ Created: {full_short_url}")

        return full_short_url

    def redirect(
        self,
        short_code: str,
        referrer: str = "direct",
        location: str = "unknown"
    ) -> str:
        """Get original URL and record analytics"""

        if short_code not in self.url_map:
            raise ValueError(f"Short code not found: {short_code}")

        shortened_url = self.url_map[short_code]
        shortened_url.record_click(referrer, location)

        return shortened_url.long_url

    def get_analytics(self, short_code: str) -> dict:
        """Get analytics for short URL"""
        if short_code not in self.url_map:
            raise ValueError(f"Short code not found: {short_code}")
        return self.url_map[short_code].get_analytics()

    def _build_short_url(self, short_code: str) -> str:
        return f"{self.domain}/{short_code}"

    def _is_valid_url(self, url: str) -> bool:
        return url.startswith(('http://', 'https://'))

    def _is_valid_alias(self, alias: str) -> bool:
        return all(c.isalnum() or c in '-_' for c in alias) and len(alias) <= 20
```

---

# 7. Autocomplete / Typeahead - Google, Amazon Search

**Used by**: Google Search, Amazon, YouTube, LinkedIn, Twitter search

**Problem**: Suggest completions as user types

**Patterns**: Trie data structure, Observer (for updates)

## Complete Implementation

```python
from typing import List, Dict, Optional
from collections import defaultdict

class TrieNode:
    """Node in Trie (prefix tree)"""

    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end_of_word = False
        self.frequency = 0
        self.word = ""

class Autocomplete:
    """
    Google-like autocomplete system using Trie

    Time Complexity:
    - Insert: O(word length)
    - Search: O(prefix length + top_k log top_k)
    - Space: O(total characters in all words)
    """

    def __init__(self):
        self.root = TrieNode()
        self.word_frequencies: Dict[str, int] = defaultdict(int)

    def add_word(self, word: str, frequency: int = 1):
        """Add word to autocomplete dictionary"""
        word = word.lower().strip()

        if not word:
            return

        # Update frequency
        self.word_frequencies[word] += frequency

        # Insert into Trie
        node = self.root

        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        node.is_end_of_word = True
        node.word = word
        node.frequency = self.word_frequencies[word]

    def search(self, prefix: str, top_k: int = 10) -> List[tuple]:
        """
        Get top k suggestions for prefix

        Returns: List of (word, frequency) tuples
        """
        prefix = prefix.lower().strip()

        if not prefix:
            return []

        # Find prefix node
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []  # No suggestions
            node = node.children[char]

        # Collect all words with this prefix
        suggestions = []
        self._collect_words(node, suggestions)

        # Sort by frequency (descending)
        suggestions.sort(key=lambda x: x[1], reverse=True)

        return suggestions[:top_k]

    def _collect_words(self, node: TrieNode, results: List[tuple]):
        """DFS to collect all words in subtree"""
        if node.is_end_of_word:
            results.append((node.word, node.frequency))

        for child in node.children.values():
            self._collect_words(child, results)

class AutocompleteSystem:
    """
    Production autocomplete like Google Search

    Features:
    - Real-time suggestions
    - Frequency-based ranking
    - Query history learning
    """

    def __init__(self):
        self.autocomplete = Autocomplete()
        self.user_searches: Dict[str, int] = defaultdict(int)

    def add_corpus(self, words: List[str], frequencies: List[int] = None):
        """Add dictionary/corpus of words"""
        if frequencies is None:
            frequencies = [1] * len(words)

        for word, freq in zip(words, frequencies):
            self.autocomplete.add_word(word, freq)

    def record_search(self, query: str):
        """Record user search to learn from behavior"""
        query = query.lower().strip()

        if query:
            self.user_searches[query] += 1
            # Add to autocomplete with boosted frequency
            self.autocomplete.add_word(query, frequency=5)

    def get_suggestions(self, prefix: str, limit: int = 10) -> List[str]:
        """Get autocomplete suggestions"""
        suggestions = self.autocomplete.search(prefix, top_k=limit)
        return [word for word, freq in suggestions]

# Demo
def demo_autocomplete():
    """Simulate Google-like autocomplete"""

    print("="*70)
    print("AUTOCOMPLETE / TYPEAHEAD (Google Search)")
    print("="*70)

    system = AutocompleteSystem()

    # Add programming terms corpus
    programming_terms = [
        "python", "python tutorial", "python programming",
        "javascript", "javascript framework", "javascript tutorial",
        "java", "java spring boot", "java tutorial",
        "react", "react hooks", "react native",
        "angular", "angular tutorial",
        "vue", "vue.js tutorial",
        "typescript", "typescript tutorial",
        "docker", "docker compose", "docker tutorial",
        "kubernetes", "kubernetes tutorial",
        "aws", "aws lambda", "aws ec2"
    ]

    # Add with simulated search frequencies
    frequencies = [1000, 500, 300, 800, 400, 350, 600, 300, 250,
                   900, 700, 500, 400, 300, 350, 300, 450, 350,
                   550, 400, 350, 700, 500, 600]

    system.add_corpus(programming_terms, frequencies)

    # Scenario 1: User types "pyt"
    print("\n📝 User types: 'pyt'")
    suggestions = system.get_suggestions("pyt", limit=5)
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")

    # Scenario 2: User types "java"
    print("\n📝 User types: 'java'")
    suggestions = system.get_suggestions("java", limit=5)
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")

    # Scenario 3: Learning from user behavior
    print("\n📝 User searches for 'python machine learning'")
    system.record_search("python machine learning")
    system.record_search("python machine learning")
    system.record_search("python machine learning")

    print("\n📝 Now 'pyt' suggestions updated:")
    suggestions = system.get_suggestions("pyt", limit=5)
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")

if __name__ == "__main__":
    demo_autocomplete()
```

**Design Decisions**:
- ✅ Trie data structure for efficient prefix search
- ✅ Frequency-based ranking (popular first)
- ✅ Learning from user behavior
- ✅ O(prefix length) search time

---

This covers examples 6-7. The file REAL-COMPANY-EXAMPLES-PART2.md has been created with URL Shortener and Autocomplete examples. Would you like me to continue with the remaining 3 examples (Retry with Exponential Backoff, Distributed Cache, and Event-Driven Architecture)?
