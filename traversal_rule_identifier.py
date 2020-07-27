import logging
import stanza
from bs4 import BeautifulSoup
logging.basicConfig(level=logging.DEBUG)
# This class gives the match rule for traversal for template given parsed beautiful soup object and author_name
# and given a traversal rule identify the author
class TraversalRule:
    NER_TAG_PERSON = "PERSON"
    nlp = stanza.Pipeline(lang='en', processors='tokenize,ner')

    def __init__(self, parsed_page, author_name, traversal_rule):
        self.parsed_page = parsed_page
        self.author_name = author_name
        self.traversal_rule = list()
        if traversal_rule:
            self.traversal_rule = traversal_rule

    # https://stackoverflow.com/questions/54265391/find-all-end-nodes-that-contain-text-using-beautifulsoup4
    def mark_if_leaf_with_text(self, node):
        if node.name in ["style", "script", "link", "meta"]:
            return False
        if not node.text:
            return False
        elif len(node.find_all(text=False)) > 0:  # no other tags inside other than text
            return False
        node.leaf = True
        return False

    def is_leaf_nodes_with_people(self, node):
        if not node.leaf:
            return False
        text = node.text
        processed_text = self.nlp(text)
        no_of_entities = len(processed_text.entities)
        people = [ent for ent in processed_text.entities if ent.type == self.NER_TAG_PERSON]
        no_of_people = len(people)
        self.candidates = list()
        if no_of_people > 0:
            node.no_of_people = no_of_people
            node.no_of_entities = no_of_entities
            node.people = people
            return True
        return False

    def find_leaf_nodes_with_people(self, node):
        self.mark_if_leaf_with_text(node)
        return self.is_leaf_nodes_with_people(node)

    def find_candidates(self):
        logging.info("Finding Candidate Authors")
        # Use stanza to identify people in text, the nodes containing them and traversal for the leaf nodes
        candidate_author_nodes_details = self.parsed_page.find_all(self.find_leaf_nodes_with_people)
        candidate_authors = list()
        for node in candidate_author_nodes_details:
            candidate_author = dict()
            # This condition may not hold
            if node.no_of_people == 1:
                candidate_author['author_entity'] = node.people[0].text
                candidate_author['ancestors'] = [parent.name for parent in node.parents]
                candidate_author['node_name'] = node.name
                candidate_authors.append(candidate_author)
        self.candidates = candidate_authors

    def pick_traversal_from_author(self):
        logging.info("Picking the traversal rule given author")
        for candidate in self.candidates:
            candidate_author_name = candidate['author_entity']
            normal_name = self.get_normal_name()
            logging.info("Candidate Author Name: {}, normal name {}".format(candidate_author_name, normal_name))
            if candidate_author_name == self.author_name or candidate_author_name == normal_name:
                self.traversal_rule = candidate['ancestors']

    def get_author_from_traversal(self):
        logging.info("Picking the author from candidates based on the traversal rule")

        self.find_candidates()
        candidates = self.candidates
        if candidates:
            for candidate in candidates:
                if candidate['ancestors'] == self.traversal_rule:
                    return candidate['author_entity']

        return None


    def get_normal_name(self):
        if "," in self.author_name:
            split = self.author_name.split(",")
            not_last_name = split[1]
            last_name = split[0]
            normal_name = not_last_name + " " + last_name
            return normal_name.strip()
        return "None"



if __name__ == "__main__":
    with open("./resources/linkedin-origin-ab-testing-nicolai-kramer-jakobsen.html", "r", encoding="UTF-8") as fp:
        html_content = fp.read()

    soup = BeautifulSoup(html_content, 'lxml')
    soup = BeautifulSoup(soup.prettify('utf-8'), 'lxml')  # some inputs are so messy that they affect the output
    t_rule = TraversalRule(soup, "Nicolai Kramer Jakobsen", None)
    t_rule.pick_traversal_from_author()
    print(t_rule.traversal_rule)