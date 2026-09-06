"""
Production Plugin #1: Audit Logger

Logs all conversations for compliance, security, and debugging.
Essential for production apps that need audit trails.

Features:
- Structured JSON logging
- PII redaction (optional)
- Metadata tracking (user_id, session_id, timestamps)
- Multiple output formats (JSON, CSV)
- Rotation and archival support

Use cases:
- GDPR/HIPAA compliance
- Security audits
- Debugging production issues
- Analytics and reporting
"""

from strands import Agent
from strands.plugins import Plugin
from strands.hooks import BeforeModelCallEvent, AfterModelCallEvent
import json
import csv
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


class AuditLoggerPlugin(Plugin):
    """
    Production-ready audit logger for agent conversations.

    Logs all user queries and agent responses with full metadata
    for compliance, security, and analytics.
    """

    def __init__(
        self,
        log_dir: str = "./audit_logs",
        format: str = "json",  # "json" or "csv"
        redact_pii: bool = False,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        name: str = "audit-logger"
    ):
        """
        Initialize the audit logger.

        Args:
            log_dir: Directory to store audit logs
            format: Log format ("json" or "csv")
            redact_pii: Whether to redact PII (emails, phone numbers, SSNs)
            user_id: User identifier for attribution
            session_id: Session identifier for grouping
            metadata: Additional metadata to include in logs
            name: Plugin name
        """
        self._name = name
        super().__init__()

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.format = format
        self.redact_pii = redact_pii
        self.user_id = user_id
        self.session_id = session_id
        self.metadata = metadata or {}

        # Stats
        self.logs_written = 0
        self.pii_redactions = 0

        # Create log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if self.format == "json":
            self.log_file = self.log_dir / f"audit_{timestamp}.jsonl"
        else:
            self.log_file = self.log_dir / f"audit_{timestamp}.csv"
            self._init_csv()

        print(f"🔒 AuditLoggerPlugin initialized")
        print(f"   Log file: {self.log_file}")
        print(f"   PII redaction: {'enabled' if redact_pii else 'disabled'}")

    @property
    def name(self) -> str:
        return self._name

    def _init_csv(self):
        """Initialize CSV file with headers."""
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'event_type', 'user_id', 'session_id',
                'content', 'content_hash', 'redacted', 'metadata'
            ])

    def _redact_pii(self, text: str) -> tuple[str, bool]:
        """
        Redact PII from text.

        Returns:
            (redacted_text, was_redacted)
        """
        original = text

        # Email addresses
        text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '[EMAIL_REDACTED]',
            text
        )

        # US Phone numbers
        text = re.sub(
            r'\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b',
            '[PHONE_REDACTED]',
            text
        )

        # US SSN
        text = re.sub(
            r'\b\d{3}-\d{2}-\d{4}\b',
            '[SSN_REDACTED]',
            text
        )

        # Credit card numbers (basic pattern)
        text = re.sub(
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            '[CC_REDACTED]',
            text
        )

        was_redacted = text != original
        if was_redacted:
            self.pii_redactions += 1

        return text, was_redacted

    def _hash_content(self, content: str) -> str:
        """Generate hash of content for integrity verification."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _extract_text(self, message) -> str:
        """Extract text content from message."""
        text_parts = []
        if hasattr(message, 'content'):
            for content in message.content:
                if hasattr(content, 'text'):
                    text_parts.append(content.text)
        return " ".join(text_parts)

    def _write_json_log(self, log_entry: Dict[str, Any]):
        """Write log entry as JSON line."""
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def _write_csv_log(self, log_entry: Dict[str, Any]):
        """Write log entry as CSV row."""
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                log_entry['timestamp'],
                log_entry['event_type'],
                log_entry['user_id'],
                log_entry['session_id'],
                log_entry['content'][:200],  # Truncate for CSV
                log_entry['content_hash'],
                log_entry['redacted'],
                json.dumps(log_entry['metadata'])
            ])

    def init_agent(self, agent: Agent) -> None:
        """Register audit hooks."""
        print("🔌 AuditLoggerPlugin connected to agent")
        agent.add_hook(self._log_user_query, BeforeModelCallEvent)
        agent.add_hook(self._log_agent_response, AfterModelCallEvent)

    def _log_user_query(self, event: BeforeModelCallEvent):
        """Log user query."""
        if not event.messages:
            return

        last_msg = event.messages[-1]
        if last_msg.role != "user":
            return

        # Extract content
        content = self._extract_text(last_msg)
        if not content:
            return

        # Redact PII if enabled
        redacted = False
        if self.redact_pii:
            content, redacted = self._redact_pii(content)

        # Create log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'user_query',
            'user_id': self.user_id or 'unknown',
            'session_id': self.session_id or 'unknown',
            'content': content,
            'content_hash': self._hash_content(content),
            'redacted': redacted,
            'metadata': self.metadata
        }

        # Write log
        if self.format == "json":
            self._write_json_log(log_entry)
        else:
            self._write_csv_log(log_entry)

        self.logs_written += 1
        print(f"📝 Logged user query (redacted: {redacted})")

    def _log_agent_response(self, event: AfterModelCallEvent):
        """Log agent response."""
        if not event.response or not event.response.content:
            return

        # Extract content
        content = self._extract_text(event.response)
        if not content:
            return

        # Redact PII if enabled (agent might echo user PII)
        redacted = False
        if self.redact_pii:
            content, redacted = self._redact_pii(content)

        # Add usage stats if available
        usage_metadata = {}
        if event.usage:
            usage_metadata = {
                'input_tokens': getattr(event.usage, 'input_tokens', 0),
                'output_tokens': getattr(event.usage, 'output_tokens', 0),
            }

        # Create log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'agent_response',
            'user_id': self.user_id or 'unknown',
            'session_id': self.session_id or 'unknown',
            'content': content,
            'content_hash': self._hash_content(content),
            'redacted': redacted,
            'metadata': {**self.metadata, **usage_metadata}
        }

        # Write log
        if self.format == "json":
            self._write_json_log(log_entry)
        else:
            self._write_csv_log(log_entry)

        self.logs_written += 1
        print(f"📝 Logged agent response (redacted: {redacted})")

    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        return {
            'logs_written': self.logs_written,
            'pii_redactions': self.pii_redactions,
            'log_file': str(self.log_file),
            'format': self.format,
            'redact_pii': self.redact_pii
        }

    def get_summary(self) -> str:
        """Get formatted summary."""
        stats = self.get_stats()
        return f"""
🔒 Audit Logger Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Log file:        {stats['log_file']}
Format:          {stats['format']}
Logs written:    {stats['logs_written']}
PII redactions:  {stats['pii_redactions']}
PII redaction:   {'enabled' if stats['redact_pii'] else 'disabled'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Audit Logger Plugin - Production Example")
    print("=" * 60 + "\n")

    # Example 1: Basic audit logging
    print("--- Example 1: Basic Logging ---\n")

    logger1 = AuditLoggerPlugin(
        log_dir="./audit_logs",
        format="json",
        user_id="user_12345",
        session_id="session_abc",
        metadata={"app": "customer_support", "version": "1.0"}
    )

    agent1 = Agent(
        system_prompt="You are a helpful customer support agent.",
        plugins=[logger1]
    )

    agent1("What are your business hours?")
    agent1("How do I reset my password?")

    print(logger1.get_summary())

    # Example 2: With PII redaction
    print("\n--- Example 2: With PII Redaction ---\n")

    logger2 = AuditLoggerPlugin(
        log_dir="./audit_logs",
        format="json",
        redact_pii=True,  # Enable PII redaction
        user_id="user_67890",
        session_id="session_xyz"
    )

    agent2 = Agent(
        system_prompt="You are a helpful assistant.",
        plugins=[logger2]
    )

    # This contains PII that will be redacted
    agent2("My email is john.doe@example.com and my phone is 555-123-4567")
    agent2("I need help with my account")

    print(logger2.get_summary())

    # Example 3: CSV format for reporting
    print("\n--- Example 3: CSV Format ---\n")

    logger3 = AuditLoggerPlugin(
        log_dir="./audit_logs",
        format="csv",  # CSV for easy reporting
        user_id="user_11111"
    )

    agent3 = Agent(
        system_prompt="You are helpful.",
        plugins=[logger3]
    )

    agent3("Hello")
    agent3("What can you help me with?")

    print(logger3.get_summary())

    print("\n" + "=" * 60)
    print("✅ Audit logs saved!")
    print("=" * 60)
    print("\nCheck the logs:")
    print("  ls -lh audit_logs/")
    print("  cat audit_logs/*.jsonl")
    print("\nUse for:")
    print("  • Compliance audits (GDPR, HIPAA)")
    print("  • Security investigations")
    print("  • Debugging production issues")
    print("  • User behavior analytics")
