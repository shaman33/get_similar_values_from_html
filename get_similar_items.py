from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import re


"""
Extract similar to given keywords items from html.

__author__      = "Roman Shneer" romanshneer@gmail.com

Usage:
parse_engine=GetSimilarItems({
        'debug_text':None,  #optional - stop and print info then scraping text equal to debug_text
        'text_max_length':0, #maximal scraped text length, longer excepting
        'items_min_count':0, #minimum items should be found in list, if less items_min_count - list excepting
        'noise_words':[], #noise_words strip this words from comparing
        'char_exceptions':[], #except if char found 
        'word_exceptions':[], #except if word found
        'sensitive_percent':30 #list should contain minimum x percents 
    })    

parse_engine.set_keywords(['apple','banana','kiwi'])
items=parse_engine.get(html)     
print(set(items))

"""

class GetSimilarItems:
    config={
        'debug_text':None,
        'text_max_length':0,
        'items_min_count':0,
        'noise_words':[],
        'char_exceptions':[],
        'word_exceptions':[],
        'sensitive_percent':30
    }

    keywords=[]

    counter=0
    result=[]
    found_items=[]

    def __init__(self, config):
        for key in config.keys():
            self.config[key]=config[key]        
        pass

    def set_keywords(self, keywords):
        """
        set keywords for search similar items
        keywords: list
        """
        self.keywords=keywords

    def __sanitize_string(self, value):
        """
            prepare value for saving
            value:str
            return value:str
        """
        value=value.strip()
        # drop last point...
        if value[len(value)-1:] in [',',':','.','!']:
            value=value[:len(value)-1]        
        return value

    def __is_word_exception(self, text):
        if len(self.config['word_exceptions'])>0:
            words=self.__clear_punctuation(text).split(' ')            
            words=[w for w in words if w!='']                        
            words.sort()
            changedWords=list(set(words)-set(self.config['word_exceptions']))
            changedWords.sort()                                
            if changedWords!=words:                                                            
                return True
        return False

    def __is_char_exceptions(self, text):
        return (
            len([we for we in self.config["char_exceptions"] if text.find(we) > -1]) > 0
        )

    def __is_valid_table_cell(self, tag):
        """
        Detect if tag can be collected and new
        tag:buityfullsoup:tag
        """

        if tag.name not in [
            "td",
            "th",
        ]:
            return False

        text = self.__sanitize_string(tag.text.lower())

        if len(text) == 0:
            return False

        if (
            self.config["text_max_length"] > 0
            and len(text) > self.config["text_max_length"]
        ):
            return False

        if self.__is_char_exceptions(text):
            return False

        if self.__is_word_exception(text) == True:
            return False

        return text in self.keywords

    def __is_valid_tag(self, tag):
        """
        Detect if tag can be collected and new
        tag:buityfullsoup:tag
        """

        if tag.name in (
            "html",
            "head",
            "meta",
            "link",
            "script",
            "title",
            "style",
            "noscript",
            "img",
            "body",
            "header",
            "form",
            "table",
            "tr",
        ):
            return False

        text=self.__sanitize_string(tag.text.lower())

        if len(text)==0:
            return False

        if self.config['text_max_length'] > 0 and len(text)>self.config['text_max_length']:
            return False

        if self.__is_char_exceptions(text):
            return False        

        if self.__is_word_exception(text)==True:
            return False

        return text in self.keywords

    def __highest_index_table(self, trs):
        """
        trs: buityfullsoup::tag TRs of table
        return highestIndex:int  - index of TD where found maximum coincidences
        """
        indexRange = {}
        for tr in trs:
            for tdIndex,td in enumerate(tr.find_all("td")):                     
                indexRange[tdIndex] = indexRange.get(tdIndex,0)
                if self.__is_text_in_keywords(td.text):
                    indexRange[tdIndex] += 1
        maxValue = max(indexRange.values())
        highestIndex = list(indexRange.values()).index(maxValue)

        return highestIndex

    def __clear_punctuation(self,text):
        """
        Removes punctuation and specific characters from the input text.

        This method replaces newline characters, tabs, and a set of punctuation 
        characters (., ?, :, ;, -, #) with a single space.

        Args:
            text (str): The input string from which punctuation and specific 
            characters will be removed.

        Returns:
            str: The cleaned text with specified characters replaced by spaces.
        """
        text=re.sub("[\n\t#.?:,;-]+", " ", text)
        return text

    def __validate_append(self, text, place):
        """
        found_items:list which collecting similar items in case its not excepted by char_exceptions or word_exception
        e : buityfullsoup::tag of checking item
        place: int - used for debugging
        originalText: string - used for debugging
        return None
        """
        value = self.__sanitize_string(text)
        if self.__is_char_exceptions(value):
            return None

        if value in self.found_items or self.__strip_noise(value) in self.found_items:
            return None

        if self.config['debug_text'] is not None and value == self.config['debug_text']:
            print(text, value, place)
            exit()

        if self.__is_word_exception(value.lower()):
            return None

        self.found_items.append(value)

    def __strip_noise(self, text):
        """
        Removes noise words from the given text.

        This method iterates through a predefined list of noise words and removes
        any occurrences of these words from the input text. The resulting text is
        stripped of leading and trailing whitespace.

        Args:
            text (str): The input text from which noise words should be removed.

        Returns:
            str: The cleaned text with noise words removed.
        """
        if len(self.config['noise_words']) > 0:
            for nw in self.config['noise_words']:
                if text.find(nw) > -1:
                    text = text.replace(nw, "").strip()
        return text

    def __is_text_in_keywords(self, text):
        """
        check if text in some variations found in keywords.
        """
        text = text.lower().strip()

        if text in self.keywords:
            return True
        text = self.__strip_noise(text)
        if text in self.keywords:
            return True
        if (
            len(
                [
                    x
                    for x in self.keywords
                    if SequenceMatcher(None, text, self.__strip_noise(x)).ratio() > 90
                ]
            )
            > 0
        ):
            return True

        return False

    def fix_three_level(self, three, new_tag, outdated_tags):
        """
        Updates a hierarchical dictionary structure (`three`) by merging outdated tags into a new tag.
        Args:
            three (dict): A dictionary representing a hierarchical structure.
                          It contains nested dictionaries under the key 'childs'.
            new_tag (str): The tag to which outdated tags will be merged.
            outdated_tags (list): A list of tags that are considered outdated and
                                  whose contents will be merged into `new_tag`.
        Behavior:
            - If `new_tag` does not exist in the `three['childs']` dictionary, it will be created.
            - For each tag in `outdated_tags`, its child elements will be moved under `new_tag`.
            - If a child element already exists under `new_tag`, their child dictionaries will be merged.
            - After merging, the outdated tags will be removed from `three['childs']`.
        Example:
            Given the following structure for `three`:
            three = {
                'childs': {
                    'tag1': {'childs': {'item1': {'childs': {}}}},
                    'tag2': {'childs': {'item2': {'childs': {}}}}
                }
            }
            Calling `fix_three_level(three, 'new_tag', ['tag1', 'tag2'])` will result in:
            three = {
                'childs': {
                    'new_tag': {
                        'childs': {
                            'item1': {'childs': {}},
                            'item2': {'childs': {}}
                        }
                    }
                }
            }
        """

        three["childs"][new_tag] =  three["childs"].get(new_tag, {"childs": {}})
        for ot in outdated_tags:
            for ot_id in three["childs"][ot]["childs"].keys():
                if ot_id in three["childs"][new_tag]["childs"].keys():
                    three["childs"][new_tag]["childs"][ot_id]["childs"].update(
                        three["childs"][ot]["childs"][ot_id]["childs"]
                    )
                else:
                    three["childs"][new_tag]["childs"][ot_id] = three["childs"][ot][
                        "childs"
                    ][ot_id]

            del three["childs"][ot]

        pass

    def __compare_list(self, elements):
        """
        Compare if all elements in the list are equal.
        elements: list
        return: bool
        """
        if not isinstance(elements, list):
            raise TypeError("Input must be a list")

        if len(elements) == 0:
            return True

        try:
            first_element = elements[0]
            return all(first_element == element for element in elements)
        except Exception as e:
            raise ValueError(f"Error comparing elements: {e}")

    def __recursive_find_variety(self, three, step):
        """
        Recursively processes a hierarchical data structure (tree) to identify and handle
        patterns or varieties in the child nodes. The method modifies the tree in place
        based on specific conditions.
        Args:
            three (dict): A dictionary representing the hierarchical tree structure.
                          It is expected to have a 'childs' key containing child nodes.
            step (int): The current recursion depth or step count.
        Behavior:
            - Iterates through the child nodes of the given tree level.
            - Identifies unique tags by removing numeric suffixes from keys.
            - Handles tags containing a colon (':') by grouping similar nodes and
              comparing their child structures.
            - If similar child structures are found, modifies the tree by creating
              a new generalized tag and recursively processes the new node.
            - Continues recursion for nodes with further child nodes.
        Notes:
            - Assumes the presence of helper methods `__compare_list` and `fix_three_level`
              for comparing child structures and modifying the tree, respectively.
            - The method is designed to work with a specific tree structure format
              and may not be applicable to other formats without modification.
        """
        tags_list = list(three["childs"].keys())
        for tag in tags_list:

            if tag not in three["childs"].keys():
                continue

            unique_tags = set([re.sub("[0-9]+", "", x) for x in three["childs"].keys()])

            for ut in unique_tags:

                if tag.find(":") > -1:
                    new_tag = ut.split(":")[0] + ":*"
                    broths = [
                        x
                        for x in three["childs"].keys()
                        if re.sub("[0-9]+", "", x) == ut
                    ]

                    if len(broths) > 1:

                        if self.__compare_list(
                            [three["childs"][x]["childs"] for x in broths]
                        ):
                            self.fix_three_level(three, ut.split(":")[0] + ":*", broths)
                            self.__recursive_find_variety(
                                three["childs"][new_tag], step + 1
                            )
                        else:
                            self.__recursive_find_variety(
                                three["childs"][tag], step + 1
                            )
                    else:
                        self.__recursive_find_variety(three["childs"][tag], step + 1)

                elif len(three["childs"][tag]["childs"].keys()) > 0:
                    self.__recursive_find_variety(three["childs"][tag], step + 1)

        pass

    def __generate_path_patterns(self, paths):
        """
        Generates hierarchical path patterns from a list of paths and converts the resulting tree structure
        back into a list of paths.
        Args:
            paths (list of str): A list of string paths where each path is represented as a sequence of tags
                                 separated by " > ".
        Returns:
            list of list of str: A list of paths where each path is represented as a list of tags.
        The method performs the following steps:
        1. Parses the input paths to construct a hierarchical tree structure where each node contains its child nodes.
        2. Recursively processes the tree structure to identify variations.
        3. Converts the tree structure back into a list of paths.
        Note:
            - The method assumes that the input paths are well-formed and use " > " as the delimiter.
            - The `__recursive_find_variety` and `three_to_paths` methods are used internally to process the tree
              and generate the final list of paths.
        """
        generated_paths = {"childs": {}}
        for path in paths:
            path = path.split(" > ")
            current_object = None
            for i, tag in enumerate(path):
                if current_object is None:
                    current_object = generated_paths
                current_object["childs"] = current_object.get("childs", {"childs": {}})
                current_object["childs"][tag] = current_object["childs"].get(
                    tag, {"childs": {}}
                )
                current_object = current_object["childs"][tag]

        self.__recursive_find_variety(generated_paths, 0)
        new_paths = self.__extract_data_from_tree(generated_paths)
        return new_paths
        pass

    def __extract_data_from_tree(self, tree, step=0):
        """
        Recursively extracts data from a tree-like dictionary structure.

        Args:
            tree (dict): A dictionary representing the tree structure. It is expected to have a 'childs' key.

        Returns:
            list: A list containing the extracted data from the tree.
        """
        results = []
        for key, value in tree.get("childs", {}).items():
            current_path = [key]
            if len(value.get("childs", {})) > 0:                
                child_results = self.__extract_data_from_tree(value, step + 1)
                [results.append(current_path + child_result) for child_result in child_results]                
            else:
                results.append(current_path)                
        return results

    def __get_shared_paths(self, elements):
        """
        Generates a list of shared CSS path patterns from a collection of elements.
        This method takes a list of elements, extracts their CSS paths, sorts them,
        and generates a set of shared path patterns. The resulting patterns can be
        used for identifying common structures or relationships among the elements.
        Args:
            elements (list): A list of elements for which CSS paths are to be extracted.
        Returns:
            list: A list of shared CSS path patterns derived from the input elements.
        """        
        paths = [self.__get_css_path(element) for element in elements]
        paths.sort()
        final_paths = self.__generate_path_patterns(paths)
        return final_paths

    def __extract_recursive(self, paths, body, step):
        """
        Recursively extracts content from an HTML structure based on a list of paths.
        Args:
            paths (list): A list of strings representing the paths to traverse in the HTML structure.
                          Each path can include CSS selectors and pseudo-classes like "nth-child".
            body (BeautifulSoup): A BeautifulSoup object representing the HTML content to search within.
            step (int): The current recursion depth, used for tracking the traversal.
        Returns:
            str | list | None:
                - A string if a single element's text is extracted.
                - A list of strings if multiple elements' texts are extracted.
                - None if no matching elements are found.
        Notes:
            - If a path contains "nth-child", the function extracts the specific child element.
            - If a path contains "*", it processes all child elements.
            - The function uses non-recursive searches (`recursive=False`) for each path segment.
            - The function handles cases where multiple elements match a path and filters out None values.
        """
        if len(paths) == 0:
            return None

        path = paths.pop(0)

        len_path = len(paths)
        childId = 0
        if path.find("nth-child") > -1:
            childId = int(re.findall("[0-9]+", path.split(":")[1])[0].strip()) - 1
            path = path.split(":")[0]          
        elif path.find("*") > -1:
            childId = -1
            path = path.split(":")[0]

        content = body.find_all(path, recursive=False)
        len_content = len(content)

        if len_content == 1:
            if len(paths) > 0:               
                return self.__extract_recursive(
                    paths.copy(), content[childId], step + 1
                )
            else:
                return content[0].text
        elif len_content > 1:
            if childId == -1:
                result = []
                for c in content:

                    if len_path > 0:
                        result.append(
                            self.__extract_recursive(paths.copy(), c, step + 1)
                        )
                    else:
                        result.append(c.text)
                result = [x for x in result if x is not None]
                return result
            else:
                if len_path > 0:

                    return self.__extract_recursive(
                        paths.copy(), content[childId], step + 1
                    )
                else:
                    return content[childId].text
        else:
            if len_path > 0:                
                return self.__extract_recursive(
                    paths.copy(), content[childId], step + 1
                )
            else:
                return [c.text for c in content]

        pass

    #### experimental function
    def __grab_other(self, elements):
        """
        Processes a list of elements to extract and append items based on shared paths.

        This method filters the input elements to retain only the younger ones,
        identifies shared paths among them, and recursively extracts items from
        the body of the first element's parent. The extracted items are appended
        to the `self.result` list.

        Args:
            elements (list): A list of elements to process.

        Returns:
            None
        """
        elements = self.__keep_only_younger(elements)
        paths = list(self.__get_shared_paths(elements))
        body = elements[0].find_parents("body")[0]
        for path in paths:
            items = self.__extract_recursive(path, body, 1)
            self.result.append(items)

    def __keep_only_younger(self, elements):
        """
        Filters a list of elements to keep only the "younger" elements based on their hierarchy.
        This method groups elements by their text value and determines which elements are
        "younger" in the hierarchy. If multiple elements share the same text value, it checks
        their parent-child relationships to identify the "younger" element. If no clear
        hierarchy is found, all elements with the same text value are retained.
        Args:
            elements (list): A list of elements to be filtered. Each element is expected to
                             have a `text` attribute and a `find_parents` method.
        Returns:
            list: A list of "younger" elements after filtering.
        """
        elementsByValue = {}
        younger_elements = []

        for e in elements:
            elementsByValue[e.text] = elementsByValue.get(e.text, [])
            elementsByValue[e.text].append(e)

        for value in elementsByValue.keys():
            maxLen = len(elementsByValue[value])
            if maxLen > 1:
                smallerItem = None

                for a in elementsByValue[value]:
                    for b in elementsByValue[value]:
                        if a != b:
                            if b in a.find_parents(b.name):
                                smallerItem = a
                if smallerItem is not None:
                    younger_elements.append(smallerItem)
                else:
                    [younger_elements.append(x) for x in elementsByValue[value]]
            else:
                younger_elements.append(elementsByValue[value][0])

        return younger_elements

    def __get_element(self, node):
        """
        Generates a CSS selector for a given HTML node based on its position among siblings of the same type.

        Args:
            node (bs4.element.Tag): The HTML node for which the CSS selector is to be generated.
                                    It is expected to be a BeautifulSoup Tag object.

        Returns:
            str: A CSS selector string in the format "tag_name:nth-child(index)", where `tag_name`
                 is the name of the node's tag and `index` is its position among siblings of the same type.
        """
        # for XPATH we have to count only for nodes with same type!
        # length = len(list(node.previous_siblings)) + 1
        length = (
            len([tag for tag in list(node.previous_siblings) if tag.name == node.name])
            + 1
        )
        return "%s:nth-child(%s)" % (node.name, length)
        # if (length) > 1:
        #    return "%s:nth-child(%s)" % (node.name, length)
        # else:
        #   return node.name

    def __get_css_path(self, node):
        """
        Generates the CSS path for a given HTML node by traversing its parent elements.

        Args:
            node (BeautifulSoup element): The HTML node for which the CSS path is to be generated.

        Returns:
            str: A string representing the CSS path of the node, with elements separated by " > ".
        """
        path = [self.__get_element(node)]
        for parent in node.parents:
            if parent.name == "body":
                break
            path.insert(0, self.__get_element(parent))
        return " > ".join(path)

    def __grab_td(self, elements):
        """
        elements:list of tags
        return elements:list of tags
        """
        elements_td = [e for e in elements if e.name in ("td", "th")]
        td_parents = [e.find_parents("table")[0] for e in elements_td]
        td_parents = list(set(td_parents))

        for table in td_parents:
            table_items=[]
            trs = table.find_all("tr")
            highestIndex = self.__highest_index_table(trs)
            for tr in trs:
                tds=tr.find_all("td")                
                if len(tds)>0:                    
                    table_items.append(self.__sanitize_string(tds[highestIndex].text))
            self.result.append(table_items)

    def __compare_results(self):
        """
        Compares the results stored in `self.result` to determine if they meet certain
        criteria based on the presence of keywords and specified thresholds.
        This method iterates through each list in `self.result`, checks how many items
        in the list match the keyword criteria, and calculates the percentage of matches.
        If the number of matches and the percentage meet the specified thresholds, it
        validates and appends the remaining items that do not match the keyword criteria.
        Returns:
            None
        Attributes:
            self.result (list of lists): A collection of lists to be processed.

        Helper Methods:
            self.__is_text_in_keywords(text): Checks if the given text exists in the keywords.
            self.__validate_append(item, message): Validates and appends an item with a message.
        Notes:
            - The method ensures that the percentage of matches is less than 100%
              to exclude fully matched lists.
            - The `percent` is rounded to the nearest integer.

        result:list of lists
        """

        for collection in self.result:
            total_count = len(collection)
            new_elements = [
                item for item in collection if not self.__is_text_in_keywords(item)
            ]
            new_count = len(new_elements)
            exists_count = total_count - new_count
            percent = round(exists_count * 100 / total_count)

            if (
                exists_count > (self.config['items_min_count'] - 1)
                and percent > self.config['sensitive_percent']
                and percent < 100
            ):
                [
                    self.__validate_append(
                        r,
                        f"exists_count={exists_count} total_count={total_count} percent={percent}",
                    )
                    for r in new_elements
                ]

        return None

    def get(self, html: str):
        """
        Get similar items from html string via self.examples
        return list
        """
        soup = BeautifulSoup(html, features="html5lib")
        [ignore_tag.decompose() for ignore_tag in soup.find_all(['h1','h2','h3','h4','h5','style','script'])]       

        ## First scrape texts from TD, TH
        elements_td = soup.find_all(self.__is_valid_table_cell)
        if len(elements_td) > 0:
            elements_td = list(set(elements_td))
            self.__grab_td(elements_td)

        ## Drop table elements
        [ignore_tag.decompose() for ignore_tag in soup.find_all("table")]

        ## Then scrape not table elements
        elements = soup.find_all(self.__is_valid_tag)

        if len(elements)>0:         
            elements = list(set(elements))
            self.__grab_other(elements)

        ### compare results ###
        self.found_items = []
        self.__compare_results()
        return set(self.found_items)
