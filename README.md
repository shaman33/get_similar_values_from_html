# Extract similar values from html

"""
This Python class parses an **HTML string** and finds tags with values similar to given keywords.
For example, if an HTML document contains a list, table, or other DOM structure:

For example in html exists list, table or other DOM structure:

<ul>
<li>Apple</li>
<li>Orange</li>
<li>Kiwi</li>
<li>Pineapple</li>
.....
</ul>

Known example keywords is ['Apple','Orange'].
Then function get_items_from_html will return values in neighboring tag <li>, except values exists in keywords: ['Kiwi','Pineapple',...]


required installation of BeautifulSoup library.



## Usage:



from get_similar_items import GetSimilarItems


parse_engine=GetSimilarItems(0.1) -  set percent of sensitivity, list will be collected only if minimum 30% found in keywords


parse_engine.set_changes_map({ 'value to replace': 'new value' }) - optional: in case replacement of value required


parse_engine.set_noise_words(['fruit']) - optional: if required to try variant with out noise word.For example for "Apple fruit" script will check variants "Apple fruit" and "Apple"


parse_engine.set_char_exceptions(['#', '@', '$']) - optional: reject if one of char_exception found in string


parse_engine.set_word_exceptions(['name']) - optional: reject if one of words from word_exceptions found in words of value


parse_engine.set_max_length(50) - optional: reject values with length less then max_length, 0 - not rejecting
parse_engine.set_min_count(3) - optional: minimum items found in element, if less - all items rejecting


#parse_engine.set_debug_text('orange') - optional: debug for entering specified value


parse_engine.set_keywords(['apple', 'banana', 'kiwi']) - required: list of keywords to search in html.


items=parse_engine.get(html)   html - string, returns list of strings


print(set(items))
"""
