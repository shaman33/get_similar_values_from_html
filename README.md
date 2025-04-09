# Extract strings from similar HTML Tags from HTML document for given keywords

"""
Overall, the **GetSimilarItems** class provides a flexible and customizable way to filter and process lists of items based on various criteria, making it suitable for tasks like data cleaning, preprocessing, or similarity-based filtering.



## For example in html exists list, table or other DOM structure:

```
<ul>
        <li>Apple</li>
        <li>Orange</li>
        <li>Kiwi</li>
        <li>Pineapple</li>
        .....
    </ul>
```

Known example keywords is ['Apple','Orange'].
Then function get_items_from_html will return values in neighboring tag <li>, except values exists in keywords: ['Kiwi','Pineapple',...]


required installation of BeautifulSoup library.



## Usage:



from get_similar_items import GetSimilarItems


**parse_engine=GetSimilarItems()**

**parse_engine.set_config({

        'debug_text':None,  #optional - stop and print info then scraping text equal to debug_text
        
        'text_max_length':50, #maximal scraped text length, longer excepting
        
        'items_min_count':2, #minimum items should be found in list, if less items_min_count - list excepting
        
        'noise_words':['fruit'], #noise_words strip this words from comparing
        
        'char_exceptions':['#', '@', '$'], #except if char found 
        
        'word_exceptions':['name'], #except if word found
        
        'sensitive_percent':30 #list should contain minimum x percents 
        
    })**


**noise_words** - optional list
*Specify a list of words to be treated as "noise." These words will be ignored during the similarity comparison. For instance, if "fruit" is a noise word, the script will evaluate both "Apple fruit" and "Apple" as potential matches.*

**char_exceptions** - optional list
*Define a list of characters that, if found in a string, will cause the string to be rejected. This is helpful for filtering out unwanted items containing specific symbols like #, @, or $.*

**word_exceptions** - optional list
*Similarly, the word_exceptions - list of words that, if present in a string, will cause the string to be rejected. This is useful for excluding items containing certain undesired words.*

**text_max_length** - optional number
*The text_max_length a maximum length for the strings being processed. Strings longer than this value will be rejected. Setting this to 0 disables the length restriction.*

**items_min_count** - optional number: minimum items found in element, if less - all items rejecting
*The items_min_count - the minimum number of items that must be found in an element for it to be considered valid. If fewer items are found, the element will be rejected.*

**debug_text** - optional string
*optional debugging tool that allows you to focus on a specific value during the processing. This can be helpful for troubleshooting or testing specific cases.*

**sensitive_percent** - optional number: 0-100
*Sensitivity percentage, which determines the threshold for similarity. For example, setting the sensitivity to 0.1 means that items will only be considered similar if at least 10% of their keywords match. This allows for fine-tuning the similarity detection process.*


**parse_engine.set_keywords(['apple', 'banana', 'kiwi'])** - required: list of keywords to search in html.


**items=parse_engine.get(html)**   html - string, returns list of strings


**print(set(items))**
"""
