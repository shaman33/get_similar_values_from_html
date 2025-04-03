# Extract strings from similar HTML Tags from HTML document for given keywords

"""
Overall, the **GetSimilarItems** class provides a flexible and customizable way to filter and process lists of items based on various criteria, making it suitable for tasks like data cleaning, preprocessing, or similarity-based filtering.



## For example in html exists list, table or other DOM structure:

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


**parse_engine=GetSimilarItems(0.1)**
*The GetSimilarItems class is initialized with a sensitivity percentage, which determines the threshold for similarity. For example, setting the sensitivity to 0.1 means that items will only be considered similar if at least 10% of their keywords match. This allows for fine-tuning the similarity detection process.*

**parse_engine.set_changes_map({ 'value to replace': 'new value' })** - optional
*The set_changes_map method allows you to define a mapping of values to be replaced with new values. This is useful if you need to standardize or preprocess the input data by replacing certain terms.*

**parse_engine.set_noise_words(['fruit'])** - optional
*The set_noise_words method lets you specify a list of words to be treated as "noise." These words will be ignored during the similarity comparison. For instance, if "fruit" is a noise word, the script will evaluate both "Apple fruit" and "Apple" as potential matches.*

**parse_engine.set_char_exceptions(['#', '@', '$'])** - optional
*The set_char_exceptions method enables you to define a list of characters that, if found in a string, will cause the string to be rejected. This is helpful for filtering out unwanted items containing specific symbols like #, @, or $.*

**parse_engine.set_word_exceptions(['name'])** - optional
*Similarly, the set_word_exceptions method allows you to specify a list of words that, if present in a string, will cause the string to be rejected. This is useful for excluding items containing certain undesired words.*

**parse_engine.set_max_length(50)** - optional
*The set_max_length method sets a maximum length for the strings being processed. Strings longer than this value will be rejected. Setting this to 0 disables the length restriction.*

**parse_engine.set_min_count(3)** - optional: minimum items found in element, if less - all items rejecting
*The set_min_count method defines the minimum number of items that must be found in an element for it to be considered valid. If fewer items are found, the element will be rejected.*

**#parse_engine.set_debug_text('orange')** - optional
*Finally, the set_debug_text method is an optional debugging tool that allows you to focus on a specific value during the processing. This can be helpful for troubleshooting or testing specific cases.*

**parse_engine.set_keywords(['apple', 'banana', 'kiwi'])** - required: list of keywords to search in html.


**items=parse_engine.get(html)**   html - string, returns list of strings


**print(set(items))**
"""
