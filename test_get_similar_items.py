from get_similar_items import GetSimilarItems 

html="<html><body><ul>" \
    "<li>Kiwi</li>" \
    "<li>Pineapple</li>" \
    "<li>Banana</li>" \
    "<li>strawberry</li>" \
    "<li>cherry</li>" \
    "</ul></body><table>" \
    "<tr><td>White</td></tr>" \
    "<tr><td>Black</td></tr>" \
    "<tr><td>Brown</td></tr>" \
    "<tr><td>Red</td></tr>" \
    "<tr><td>Red</td></tr>" \
    "<tr><td>Blue</td></tr>" \
    "<tr><td>Pink</td></tr>" \
    "</table>" \
    "<p><em>Link1</em>, <em>Link2</em>....what ever <em>Link3</em>...<em>Link4</em>....<em>Link5</em>..<em>Link6</em><p>" \
    "</html>"

def test_list():
   
    parse_engine=GetSimilarItems(10)
    parse_engine.set_keywords(['apple','banana'])
    items=parse_engine.get_items_from_html(html)  
    assert len(items)==4

def test_table():
   
    parse_engine=GetSimilarItems(10)
    parse_engine.set_keywords(['read','pink'])
    items=parse_engine.get_items_from_html(html)  
    assert len(items)==5

def test_others():
    parse_engine=GetSimilarItems(10)
    parse_engine.set_keywords(['link6','link4'])
    items=parse_engine.get_items_from_html(html)  
    assert len(items)==4

if __name__ == "__main__":
    test_list()
    test_table()
    test_others()
    print("Everything passed")