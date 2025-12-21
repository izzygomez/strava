import requests


def send_notification(topic_url, message, title=None, priority="default", tags=None):
    """
    Send a notification to ntfy.sh.

    Args:
        topic_url: The full ntfy.sh topic URL
        message: The notification message body
        title: Optional notification title (default: None)
        priority: Priority level - "min", "low", "default", "high", or "max" (default: "default")
        tags: Optional list of tags/emojis (e.g., ["tada", "rocket"])

    Returns:
        True if notification was sent successfully, False otherwise
    """
    try:
        # ntfy.sh expects the message as request body and metadata as headers
        headers = {}

        if title:
            headers["Title"] = title
        if priority:
            headers["Priority"] = priority
        if tags:
            headers["Tags"] = ",".join(tags)

        response = requests.post(
            topic_url,
            data=message.encode("utf-8"),
            headers=headers,
        )
        response.raise_for_status()
        print(f"\nNotification sent successfully to {topic_url}")
        return True
    except requests.exceptions.RequestException as e:
        # Non-blocking - just log the error and continue
        print(f"\nWarning: Failed to send notification to ntfy.sh: {e}")
        return False
