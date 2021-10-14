import unittest
from intersection_finding import *

class TestIntersectionFinder(unittest.TestCase):
    def test1(self):
        finder = IntersectionFinder()
        finder.add_text_to_graph('A B C A C D E A')
        finder.add_text_to_graph('B C A D E C')
        intersections = finder.get_intersections('K B C A D E C F G A B C')
        self.assertTrue(len(intersections) == 2)
        self.assertTrue(intersections[0]['text'] == 'B C A D E C')
        self.assertTrue(intersections[0]['sources_indexes'] == {1})
        self.assertTrue(intersections[1]['text'] == 'A B C')
        self.assertTrue(intersections[1]['sources_indexes'] == {0})

if __name__ == '__main__':
    unittest.main()