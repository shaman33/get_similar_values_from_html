from bs4 import BeautifulSoup
"""
Extract similar to given keywords items from html.

__author__      = "Roman Shneer" romanshneer@gmail.com

Usage:
parse_engine=GetSimilarItems(30)    


parse_engine.set_changes_map({'value to replace':'new value' })
parse_engine.set_noise_words(['fruit'])    
parse_engine.set_char_exceptions(['#','@','$'])
parse_engine.set_word_exceptions(['name'])
parse_engine.set_max_length(50)

#parse_engine.set_debug_text('orange')

parse_engine.set_keywords(['apple','banana','kiwi'])
items=parse_engine.get_items_from_html(html)     
print(set(items))

"""

class GetSimilarItems:
    debugText=None
    max_length=0
    changes_map={}
    keywords=[]
    noise_words=[]
    char_exceptions=[]
    word_exceptions=[]

    def __init__(self, sensetivePercent=30):
              
        self.sensetivePercent=sensetivePercent
        self.found_items=[]
        """
        sensetivePercent: int - sensetivity of recursive search minimum percent's count of items required for positive response
        """
        pass

    def set_keywords(self, keywords):
        """
        set keywords for search similar items
        keywords: list
        """
        self.keywords=keywords

    def set_debug_text(self, debugText):
        """
        stop execution and show tag if debugText processing
        debugText:str
        """
        self.debugText=debugText

    def set_changes_map(self, changes_map):
        """
        define changes dist
        changes_map: dist valueToReplace:valueReplacment 
        (before comparing with examples) 
        """
        self.changes_map=changes_map
        pass
    
    def set_noise_words(self, noise_words):
        """ 
        noise_words: list of strings which should be removed in case value not found in examples 
        (before comparing with examples) 
        """
        self.noise_words=noise_words
        pass


    def set_char_exceptions(self, char_exceptions):
        """ 
        char_exceptions: list of strings - value will be skipped in case char will be found in text of value
        (before comparing with examples) 
        """
        self.char_exceptions=char_exceptions
        pass

    def set_word_exceptions(self, word_exceptions):
        """ 
        word_exceptions: list of strings - value will be skipped in case word will be found in words of value
        (before comparing with examples) 
        """
        self.word_exceptions=word_exceptions
        pass

    def set_max_length(self, max_length):
        """
        define max length of value - optimizate perfomance
        max_length:int
        """
        self.max_length=max_length
    


    def __is_new_record(self, name):  
        """
        Detect if value exists in any variations in keywords list of already collected to found_items
        name:str
        return Boolean
        """
        keywords=self.keywords
        found_items=[e.lower() for e in self.found_items]

       
        name=name.lower().strip()
        if name in self.changes_map:
            name=self.changes_map[name] 
           
        if name in keywords or name in found_items:
            return False

       
        
        if len(self.noise_words)>0:
            for nw in self.noise_words:              
                if name.find(nw)>-1:                                        
                    name1=name.replace(nw,'').strip()                           
                   
                    if name1 in keywords or name1 in found_items:                     
                        return False
                        
                    if name1[len(name1)-1:]!='s':
                        name1=name1+'s'
                        if name1 in keywords or name1 in found_items:
                            return False     
                                                                   
        if name.find('(')>-1:
            name2=name[0:name.find('(')].strip()
            if name2 in keywords or name2 in found_items:
                return False      
        
        ### Add s to end of world
        if name[len(name)-1:]!='s':            
            name3=name+'s'
            if name3 in keywords or name3 in found_items:
                return False
        else:
            ### drop s to end of world
            name4=name[0:len(name)-1]
            if name4 in keywords or name4 in found_items:
                return False
        
        return True
    

   

    def __is_valid_tag(self, tag):
        """
        Detect if tag can be collected and new
        tag:buityfullsoup:tag
        """

        if tag.name in ['html','head','meta','link','script','title','style','noscript','img','body','header','form','table','tr']:
            return False
        text=tag.text.lower().strip()
        
        if len(text)==0:
            return False
        
        if self.max_length > 0:
            if len(text)>self.max_length:
                return False
            
        return self.__is_new_record(text)==False
                      
    
    def get_items_from_html(self, html: str):
        """
        Get similar items from html string via self.examples
        return list
        """
        
        soup = BeautifulSoup(html, features="html.parser")
       
        
      
        def __highest_index_table(trs):
            """
            trs: buityfullsoup::tag TRs of table
            return highestIndex:int  - index of TD where found maximum coincidences
            """
            indexRange={}
            for tr in trs:
                tds=tr.find_all('td')
                for tdIndex in range(0,len(tds)):
                    td=tds[tdIndex]
                    
                    if tdIndex not in indexRange:
                        indexRange[tdIndex]=0
                    if self.__is_new_record(td.text)==False:
                        indexRange[tdIndex]+=1
            maxValue=max(indexRange.values());                     
            highestIndex=list(indexRange.values()).index(maxValue)   

            return highestIndex
        

        def __validate_append(e, place):
            """
            found_items:list which collecting similar items in case its not excepted by char_exceptions or word_exception
            e : buityfullsoup::tag of checking item
            place: int - used for debugging
            originalText: string - used for debugging
            return None
            """ 
            broken=False              
            for we in self.char_exceptions:              
                if e.text.lower().find(we)>-1:
                    broken=True
            if broken==True:
                 return None
            
            if self.debugText is not None and e.text==self.debugText:
                print(e,place)
                exit()
            
            if len(self.word_exceptions)>0:

                words=e.text.lower().split(' ')
                words=[w.replace(':','').replace('.','').replace(',','').replace(';','').replace('#','').replace('-','') for w in words]                               
                words.sort()
                changedWords=list(set(words)-set(self.word_exceptions))
                changedWords.sort()                
                if changedWords==words:                    
                    self.found_items.append(e.text)
                
                return None
                
            self.found_items.append(e.text)
       
        def __filter_via_examples(elements, found=True):
            """
            Filter elements via self.exaples
            elements: buityfullsoup list
            found: True - exists in examples, False not in examples
            return filtered:buityfullsoup list
            """
            if found==True:
                filtered = [x for x in elements if self.__is_new_record(x.text)==False]                      
            else: 
                filtered = [x for x in elements if self.__is_new_record(x.text)]                      
            return filtered
        
        def __find_rich_parent(e, getParent=False):
            """
            Recursive search children contains in examples
            e: buityfullsoup:list
            return children :buityfullsoup::list
            """
            if e.parent==None or e.parent.name=='body':
                return None
            children=e.parent.find_all(e.name)
            found_len=len(__filter_via_examples(children,True))
            percent=found_len*100/len(children)
           
                                            
            if percent > self.sensetivePercent:
                if getParent==True:
                    
                    return e.parent
                else:                    
                    return children
            else: 
                return __find_rich_parent(e.parent, getParent)
            

        def __keep_only_younger(elements):
            elementsByValue={}
            younger_elements=[]

            for e in elements:
                if e.text not in elementsByValue.keys():
                    elementsByValue[e.text]=[]            
                elementsByValue[e.text].append(e)
        
            for value in elementsByValue.keys():
                    
                maxLen=len(elementsByValue[value])
                if maxLen>1:
                    smallerItem=None
                    
                    for a in elementsByValue[value]:
                        for b in elementsByValue[value]:
                            if a != b:                                                        
                                if b in a.find_parents(b.name):
                                    smallerItem=a
                    if smallerItem is not None:
                        younger_elements.append(smallerItem)
                    else: 
                        for x in elementsByValue[value]:
                            younger_elements.append(x)                                            
                else:
                     younger_elements.append(elementsByValue[value][0])

            return younger_elements
    

        
        [ignore_tag.decompose() for ignore_tag in soup.find_all(['h1','h2','h3','h4','h5'])]       
       
        elements=soup.find_all(self.__is_valid_tag)
       
        elements=list(set(elements))

        elements=__keep_only_younger(elements)
          
        def get_tags(items, tag, negative=False):
            if negative is True:
                return [e for e in items if not (e.name==tag or  e.parent.name==tag or  e.parent.parent.name==tag)]
            else:                
                return [e for e in items if (e.name==tag or  e.parent.name==tag or  e.parent.parent.name==tag)]

        self.found_items=[]
        ## li parsing
        elements_li=get_tags(elements,'li') 
        li_parents=[e.find_parents(['ul','ol'])[0] for e in elements_li]
        li_parents=list(set(li_parents))
        for ul in li_parents:
            lis=ul.find_all('li')
            validated=__filter_via_examples(lis,True)
           
            percent=len(validated)*100/len(lis)
            if percent > self.sensetivePercent:
                for c in __filter_via_examples(lis,False):
                     __validate_append(c,2)
                         
        elements=get_tags(elements,'li',True)
        #### td parsing
        elements_td=get_tags(elements,'td')
        td_parents=[e.find_parents('table')[0] for e in elements_td]
        td_parents=list(set(td_parents))
        for table in td_parents:
            trs=table.find_all('tr')
            highestIndex=__highest_index_table(trs)
            tdsFound=[]            
            for tr in trs:           
                tds=tr.find_all('td')
                tdsFound.append(tds[highestIndex])
            
            validatedTds=__filter_via_examples(tdsFound,True)
            percentTds=len(validatedTds) * 100 / len(tdsFound)
            if percentTds > self.sensetivePercent:
                for td in __filter_via_examples(tdsFound,False):                 
                    __validate_append(td,1)
        
        elements=get_tags(elements,'td',True)

        ## other items - search best parents   
        tags=set([e.name for e in elements])
       
        elementsParents=[e for e in [__find_rich_parent(e, True) for e in elements]  if e is not None]
        elementsParents=list(set(elementsParents))
      
        for ep in elementsParents:
            found=ep.find_all(tags)
            exists=__filter_via_examples(found,True)
            percent=len(exists) * 100 / len(found)
            if percent > self.sensetivePercent and percent<100:
                for it in __filter_via_examples(found,False):                       
                    __validate_append(it,3)
            
        return set(self.found_items)