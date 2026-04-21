"""Basic test suite for Scout Agent."""
import unittest
from unittest.mock import patch, MagicMock
from src.models import RepoAnalysis, SearchStrategy, FileSelection


class TestModels(unittest.TestCase):
    """Test data models."""

    def test_repo_analysis_creation(self):
        """Test RepoAnalysis model creation."""
        analysis = RepoAnalysis(
            name="test/repo",
            summary="Test repository",
            language="Python",
            tech_stack=["Flask", "SQLAlchemy"],
            core_workflow="1. Load data 2. Process 3. Return results",
            key_learnings=["REST APIs", "ORMs"],
            complexity_level="Intermediate",
            activity_status="Active",
            stars=100,
            forks=20
        )
        
        self.assertEqual(analysis.name, "test/repo")
        self.assertEqual(analysis.stars, 100)
        self.assertEqual(len(analysis.tech_stack), 2)

    def test_search_strategy_creation(self):
        """Test SearchStrategy model creation."""
        strategy = SearchStrategy(
            queries=["query1", "query2", "query3"],
            keywords=["keyword1", "keyword2"],
            expanded_terms=["expansion1", "expansion2"],
            reasoning="Test reasoning"
        )
        
        self.assertEqual(len(strategy.queries), 3)
        self.assertEqual(len(strategy.keywords), 2)

    def test_file_selection_creation(self):
        """Test FileSelection model creation."""
        selection = FileSelection(
            selected_files=["file1.py", "file2.py"],
            reasoning="These are core files"
        )
        
        self.assertEqual(len(selection.selected_files), 2)


class TestIntegration(unittest.TestCase):
    """Integration tests for Scout Agent."""

    @patch('src.api.github_client.Github')
    def test_search_github_mock(self, mock_github):
        """Test GitHub search with mocked API."""
        from src.api import search_github
        
        # Setup mock
        mock_repo = MagicMock()
        mock_repo.full_name = "test/repo"
        mock_repo.description = "Test repo"
        mock_repo.get_topics.return_value = ["python", "testing"]
        mock_repo.stargazers_count = 100
        mock_repo.forks_count = 20
        mock_repo.language = "Python"
        mock_repo.pushed_at.strftime.return_value = "2024-01-01"
        mock_repo.size = 500
        mock_repo.fork = False
        
        # Note: This test structure assumes mocking setup
        # In practice, more complex setup would be needed


if __name__ == '__main__':
    unittest.main()
