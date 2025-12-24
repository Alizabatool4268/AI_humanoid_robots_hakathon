import sys
import os
# Add the src directory to the path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from qdrant_client import QdrantClient
from config.settings import Settings

def test_query_format():
    settings = Settings()
    client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY, timeout=30.0)
    # Test with a simple query to see what format we get
    results = client.query_points(
        collection_name=settings.COLLECTION_NAME,
        query=[0.0] * 1024,  # dummy vector
        limit=1,
        with_payload=True
    )
    print('Results type:', type(results))
    print('Results:', results)
    if hasattr(results, 'points'):
        print('Has points attribute')
        points = results.points
        print('Points type:', type(points))
        if points:
            result = points[0]
            print('First point type:', type(result))
            print('First point:', result)
            if hasattr(result, '__dict__'):
                print('Attributes:', result.__dict__.keys())
            if hasattr(result, 'id'):
                print('Has id attribute')
            if hasattr(result, 'score'):
                print('Has score attribute')
            if hasattr(result, 'payload'):
                print('Has payload attribute')

if __name__ == "__main__":
    test_query_format()