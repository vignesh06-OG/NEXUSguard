import pytest
from unittest.mock import Mock

from agent_core import post_review_to_github, format_review_markdown


def test_post_review_creates_comment_when_none():
    pr = Mock()
    pr.get_issue_comments.return_value = []
    pr.create_issue_comment = Mock()

    comment_body = "## Test Review"
    post_review_to_github(pr, comment_body)

    pr.create_issue_comment.assert_called_once_with(comment_body)


def test_post_review_edits_existing_nexusguard_comment():
    pr = Mock()
    comment = Mock()
    comment.user = Mock()
    comment.user.login = "NEXUSguard"
    comment.body = "old"
    comment.edit = Mock()

    pr.get_issue_comments.return_value = [comment]
    pr.create_issue_comment = Mock()

    comment_body = "## Updated"
    post_review_to_github(pr, comment_body)

    comment.edit.assert_called_once_with(comment_body)
    pr.create_issue_comment.assert_not_called()


def test_post_review_edits_on_marker_in_body():
    pr = Mock()
    comment = Mock()
    comment.user = Mock()
    comment.user.login = "someoneelse"
    comment.body = "This was posted by NEXUSguard bot"
    comment.edit = Mock()

    pr.get_issue_comments.return_value = [comment]
    pr.create_issue_comment = Mock()

    post_review_to_github(pr, "body")

    comment.edit.assert_called_once()
    pr.create_issue_comment.assert_not_called()


def test_format_review_markdown_table_and_truncate():
    short = "line1\nline2\nline3"
    md = format_review_markdown(short, 4, "Title", "http://url")

    assert "| Risk Score | Summary |" in md
    assert "|---:|---|" in md
    assert "<br/>" in md
    assert "line1<br/>line2<br/>line3" in md

    long = "a" * 13000
    md2 = format_review_markdown(long, 9, "T", "u")
    assert "*(truncated)*" in md2
    assert "| 9/10 |" in md2
