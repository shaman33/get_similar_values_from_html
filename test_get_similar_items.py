from get_similar_items import GetSimilarItems

html = (
    "<html><body>"
    "<div class='main'>"
    "<div class='correct'>"
    "<div><em>Name of link1</em><em>Link1</em><em>garbage</em></div> "
    "<div><em>Name of link2</em><em>Link2</em><em>garbage</em></div>"
    "....what ever <div><em>Name of link3</em><em>Link3</em><em>garbage</em></div>..."
    "<div><em>Name of link4</em><em>Link4</em><em>garbage</em></div>...."
    "<div><em>Name of link5</em><em>Link5</em></div>.."
    "<div><em>Name of link8</em><em>Link6</em><span>garbage</span></div>"
    "<div><em>Name of link7</em><em>Link7</em><span>garbage</span></div>"
    "<b>Bold</b>"
    "</div>"
    "<div><div class='also_correct'><a href=''>Link1</a><a href=''>Link2</a><a href=''>Link3</a><a href=''>Link4</a><a href=''>Link5</a><a href=''>Link6</a><a href=''>Link7</a><a href=''>Link8</a><a href=''>Link9</a><a href=''>Link10</a><a href=''>Link11</a></div></div>"
    "</div>"
    "<table>"
    "<tbody>"
    "<tr><th>Colors</th><th>value header</th></tr>"
    "<tr><td>pink</td><td>value</td></tr>"
    "<tr><td>blue</td><td>value</td></tr>"
    "<tr><td>gray</td><td>value</td></tr>"
    "<tr><td>black</td><td>value</td></tr>"
    "<tr><td>black</td><td>value</td></tr>"
    "<tr><td>white</td><td>value</td></tr>"
    "<tr><td>purple</td><td>value</td></tr>"
    "</tbody>"
    "</table>"
    "</body></html>"
)



def test_table():

    parse_engine = GetSimilarItems({
        'sensitive_percent':10,
        'items_min_count':1
    })
  
    parse_engine.set_keywords(["read", "pink"])
    
    items = parse_engine.get(html)
    print("items", items)
    assert len(items) == 5


def test_others():
    parse_engine = GetSimilarItems({
        'sensitive_percent':10,
        'items_min_count':1
    })
   
    parse_engine.set_keywords(["link2", "link1", "link3", "link4"])
    items = parse_engine.get(html)
    print("items", items)
    assert len(items) == 7


if __name__ == "__main__":    
    test_table()
    test_others()
    print("Everything passed")
