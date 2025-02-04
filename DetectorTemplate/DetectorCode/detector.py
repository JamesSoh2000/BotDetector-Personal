from abc_classes import ADetector
from teams_classes import DetectionMark
from collections import Counter

class Detector(ADetector):
    def detect_bot(self, session_data):
        # todo logic
        # Example:
        marked_account = []


        for user in session_data.users:
            user_posts = [post for post in session_data.posts]
            features = {"post_repetition" : self._check_post_repetition(user_posts)}

            confidence = int(features["post_repetition"] * 1000)
            is_bot = confidence > 30
            
            marked_account.append(DetectionMark(user_id=user['id'], confidence = 100, bot=is_bot))

        return marked_account
    
    def _check_post_repetition(self, posts):
        """Check for duplicate/similar posts by text we are given"""
        texts = [p['text'] for p in posts]
        duplicate_ratio = sum(count for text, count in Counter(texts).items() 
                            if count > 1) / len(texts)
        return min(duplicate_ratio * 2, 1.0)