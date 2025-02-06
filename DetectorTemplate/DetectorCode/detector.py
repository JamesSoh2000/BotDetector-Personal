from abc_classes import ADetector
from teams_classes import DetectionMark
from collections import Counter
from datetime import datetime
import re

class Detector(ADetector):
    def detect_bot(self, session_data):
        marked_account = []

        for user in session_data.users:
            user_posts = [post for post in session_data.posts]
            features = {
                "post_repetition": self._check_post_repetition(user_posts),
                "posting_interval": self._check_posting_intervals(user_posts)
            }
            # Combine features into confidence (average of both)
            combined_confidence = (features["post_repetition"] + features["posting_interval"]) / 2
            confidence = int(combined_confidence * 100)
            is_bot = confidence > 40  # Threshold can be adjusted
            
            marked_account.append(DetectionMark(
                user_id=user['id'],
                confidence=confidence,
                bot=is_bot
            ))

        return marked_account
    
    def _check_post_repetition(self, posts):
        """Check for duplicate/similar posts by text after preprocessing."""
        processed_texts = [self._preprocess_text(post['text']) for post in posts]
        text_counts = Counter(processed_texts)
        duplicate_count = sum(count for text, count in text_counts.items() if count > 1)
        total_posts = len(processed_texts)
        if total_posts == 0:
            return 0.0
        duplicate_ratio = duplicate_count / total_posts
        return min(duplicate_ratio * 2, 1.0)  # Scale and cap the ratio
    
    def _preprocess_text(self, text):
        """Normalize text by removing URLs, replacing hashtags and default_topic."""
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        # Replace hashtags with [HASHTAG]
        text = re.sub(r'#\w+', '[HASHTAG]', text)
        # Replace 'default_topic' with [TOPIC]
        text = re.sub(r'\bdefault_topic\b', '[TOPIC]', text)
        # Clean whitespace
        return re.sub(r'\s+', ' ', text).strip()
    
    def _check_posting_intervals(self, posts):
        """Check for posts made within less than 30 seconds of each other."""
        if len(posts) < 2:
            return 0.0  # Not enough posts
        
        sorted_posts = sorted(posts, key=lambda p: p['created_at'])
        short_intervals = 0
        
        for i in range(1, len(sorted_posts)):
            prev_time = self._parse_datetime(sorted_posts[i-1]['created_at'])
            curr_time = self._parse_datetime(sorted_posts[i]['created_at'])
            delta = (curr_time - prev_time).total_seconds()
            
            if delta < 30:
                short_intervals += 1
        
        total_intervals = len(sorted_posts) - 1
        interval_ratio = short_intervals / total_intervals
        return interval_ratio
    
    def _parse_datetime(self, dt_str):
        """Parse ISO datetime string, handling UTC 'Z' suffix."""
        if dt_str.endswith('Z'):
            dt_str = dt_str[:-1] + '+00:00'
        return datetime.fromisoformat(dt_str)