from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from html import escape

from src.feed_source import Post


def build_email(post: Post, matched_terms: list[str], reason: str, llm_reason: str | None = None) -> EmailMessage:
    sender = os.environ["EMAIL_FROM"]
    recipient = os.environ["EMAIL_TO"]
    cc = [item.strip() for item in os.environ.get("EMAIL_CC", "").split(",") if item.strip()]

    msg = EmailMessage()
    msg["Subject"] = f"Codex Reset Alert - {post.author}"
    msg["From"] = sender
    msg["To"] = recipient
    if cc:
        msg["Cc"] = ", ".join(cc)

    terms = ", ".join(matched_terms) if matched_terms else "None"
    llm_block = f"\nLLM classification:\n{llm_reason}\n" if llm_reason else ""
    body = f"""A monitored public X post may be related to a Codex reset.

Account: {post.author} (@{post.handle})
Published: {post.published}
URL: {post.url}

Matched terms: {terms}
Keyword reason: {reason}
{llm_block}
Post:
{post.text}
"""
    msg.set_content(body)
    html_text = escape(post.text)
    html_reason = escape(reason)
    html_llm_reason = escape(llm_reason) if llm_reason else None
    html_terms = escape(terms)
    html_url = escape(post.url)

    msg.add_alternative(
        f"""
        <html>
          <body>
            <h2>Codex Reset Alert - {post.author}</h2>
            <p>A monitored public X post may be related to a Codex reset.</p>
            <p><strong>Account:</strong> {post.author} (@{post.handle})<br>
               <strong>Published:</strong> {post.published}<br>
               <strong>URL:</strong> <a href="{html_url}">{html_url}</a></p>
            <p><strong>Matched terms:</strong> {html_terms}</p>
            <p><strong>Keyword reason:</strong> {html_reason}</p>
            {f"<p><strong>LLM classification:</strong> {html_llm_reason}</p>" if html_llm_reason else ""}
            <blockquote>{html_text}</blockquote>
          </body>
        </html>
        """,
        subtype="html",
    )
    return msg


def send_email(message: EmailMessage) -> None:
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT", "587"))
    username = os.environ["SMTP_USERNAME"]
    password = os.environ["SMTP_PASSWORD"]

    recipients = [message["To"]]
    if message.get("Cc"):
        recipients.extend([item.strip() for item in message["Cc"].split(",")])

    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message, to_addrs=recipients)
