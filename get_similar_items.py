from bs4 import BeautifulSoup
from difflib import SequenceMatcher
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
    counter=0
    result=[]
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
    
    def sanitize_string(self, value):
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

    def __is_new_record(self, name):  
        """
        Detect if value exists in any variations in keywords list
        name:str
        return Boolean
        """
        name=self.sanitize_string(name.lower())
        keywords=self.keywords
        #@found_items=[e.lower() for e in self.found_items]
             
        if name in self.changes_map:
            name=self.changes_map[name] 
        if name in keywords:
            return False
        #if name in keywords or name in found_items:
        #    return False

        
        if len(self.noise_words)>0:
            for nw in self.noise_words:              
                if name.find(nw)>-1:                                        
                    name1=name.replace(nw,'').strip()                           
                   
                    if name1 in keywords:                     
                        return False
                        
                    if name1[len(name1)-1:]!='s':
                        name1=name1+'s'
                        if name1 in keywords:
                            return False     
                                                                   
        if name.find('(')>-1:
            name2=name[0:name.find('(')].strip()
            if name2 in keywords:
                return False      
        
        ### Add s to end of world
        if name[len(name)-1:]!='s':            
            name3=name+'s'
            if name3 in keywords:
                return False
        else:
            ### drop s to end of world
            name4=name[0:len(name)-1]
            if name4 in keywords:
                return False
            
        return True
    

   

    def __is_valid_tag(self, tag):
        """
        Detect if tag can be collected and new
        tag:buityfullsoup:tag
        """

        if tag.name in ['html','head','meta','link','script','title','style','noscript','img','body','header','form','table','tr']:
            return False
         
        text=self.sanitize_string(tag.text.lower())
        
        if len(text)==0:
            return False
        
        if self.max_length > 0:
            if len(text)>self.max_length:
                return False
        
        for we in self.char_exceptions:              
            if text.find(we)>-1:
                return False
        if len(self.word_exceptions)>0:
            
            words=text.replace(':',' ').replace('.',' ').replace(',',' ').replace(';',' ').replace('#',' ').replace('-',' ').replace('\n',' ').replace('\t',' ').split(' ')
            words=[w for w in words if w!='']                        
            words.sort()
            changedWords=list(set(words)-set(self.word_exceptions))
            changedWords.sort()                                
            if changedWords!=words:                                                            
               return False
          
        return text in self.keywords

                      
    def __highest_index_table(self, trs):
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
    
    def get_items_from_html(self, html: str):
        """
        Get similar items from html string via self.examples
        return list
        """
        
      
        soup = BeautifulSoup(html, features="html5lib")
        
        

        def __validate_append(text, place):
            """
            found_items:list which collecting similar items in case its not excepted by char_exceptions or word_exception
            e : buityfullsoup::tag of checking item
            place: int - used for debugging
            originalText: string - used for debugging
            return None
            """ 
            
            broken=False              
            value=self.sanitize_string(text)
          
            for we in self.char_exceptions:              
                if value.lower().find(we)>-1:
                    broken=True
            if broken==True:
                 return None
            
           
            if value in self.found_items or strip_noise(value) in self.found_items:
                return None
            if self.debugText is not None and value==self.debugText:
                print(text,value,place)
                exit()
            if len(self.word_exceptions)>0:
                
                words=value.lower().replace(':',' ').replace('.',' ').replace(',',' ').replace(';',' ').replace('#',' ').replace('-',' ').replace('\n',' ').replace('\t',' ').split(' ')
                words=[w for w in words if w!='']                            
                words.sort()
                changedWords=list(set(words)-set(self.word_exceptions))
                changedWords.sort()                                
                if changedWords==words:   
                                                                    
                    self.found_items.append(value)                
                return None
                                     
            self.found_items.append(value)

        def strip_noise(text):
            if len(self.noise_words)>0:
                for nw in self.noise_words:                
                    if text.find(nw)>-1:
                        text=text.replace(nw,'').strip()
            return text

        def is_text_in_keywords(text):
            """
                check if text in some variations found in keywords.
            """
            text=text.lower().strip()
            
            if text in self.keywords:
                return True
            if len([x for x in self.keywords if SequenceMatcher(None, text,x).ratio()>90])>0:
                return True
            
            if len(self.noise_words)>0:

                text=strip_noise(text)
                if len([x for x in self.keywords if SequenceMatcher(None, text,x).ratio()>90])>0:
                    return True
           
            return False
        
        def __keep_only_younger(elements):
            """
            remove parents of element in elements if exists
            elements: list of tags
            return: list of tags
            """
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
       
       
        
        def __find_rich_parent(e, getParent=False):
            """
            Recursive search children contains in examples
            e: buityfullsoup:list
            return children :buityfullsoup::list
            """
            if e.parent==None or e.parent.name=='body':
                return None           
            children=e.parent.findChildren(e.name, recursive=False)
           
            if len(children)>0:
                if getParent==True:
                    
                    return e.parent
                else:                    
                    return children
            else: 
                return __find_rich_parent(e.parent, getParent)
            
            
        def get_tags(items, tag, negative=False):
            """
            items: list
            tag : bs4::tag
            """
            if negative is True:
                return [e for e in items if not (e.name==tag or  e.parent.name==tag or  e.parent.parent.name==tag)]
            else:                
                return [e for e in items if (e.name==tag or  e.parent.name==tag or  e.parent.parent.name==tag)]
            

        def grab_li(elements):
            """
            elements:list of tags
            return elements:list of tags
            """
            elements_li=get_tags(elements,'li') 
            uls=[e.find_parents(['ul','ol'])[0] for e in elements_li]
            uls=list(set(uls))
           
            for ul in uls:                
                self.result.append([self.sanitize_string(li.text) for li in ul.findChildren('li', recursive=False)])     

            return get_tags(elements,'li',True)            
        
        def grab_td(elements):
            """
            elements:list of tags
            return elements:list of tags
            """
            elements_td=get_tags(elements,'td')
            td_parents=[e.find_parents('table')[0] for e in elements_td]
            td_parents=list(set(td_parents))
            
            for table in td_parents:
                trs=table.find_all('tr')
                highestIndex=self.__highest_index_table(trs)                
                self.result.append([self.sanitize_string(tr.find_all('td')[highestIndex].text) for tr in trs])                
            return get_tags(elements,'td',True)           
        
        def grab_other(elements):
            """
            elements:list of tags
           
            """
            ep_pars=[]
            ep_tags=[]
            for e in elements:
                ep_pars.append(__find_rich_parent(e, True))
                ep_tags.append(e.name)               
            ep_pars_uniq=list(set(ep_pars))
            for p in ep_pars_uniq:
                tag=ep_tags[ep_pars.index(p)]
                children=p.findChildren(tag, recursive=False)
                if len(children)<1:
                    children=p.find_all('a')

                self.result.append([self.sanitize_string(c.text) for c in children])


        def compare_result(result):
            """
                result:list of lists
            """
            for res in result:         
                exists=[r for r in res if is_text_in_keywords(r)]
                total_count=len(res)
                exists_count=len(exists)
                percent=round(exists_count*100/total_count)                                
                if exists_count>0 and percent>self.sensetivePercent and percent<100:                   
                    [__validate_append(r,4) for r in res if not is_text_in_keywords(r)]
                                    
            return None

        

        
        [ignore_tag.decompose() for ignore_tag in soup.find_all(['h1','h2','h3','h4','h5','style','script'])]       
        
        elements=soup.find_all(self.__is_valid_tag)     
        elements=list(set(elements))
        elements=__keep_only_younger(elements)
        
        

        self.found_items=[]
        elements=grab_td(elements)       
        elements=grab_li(elements)                
        grab_other(elements)
        
        
        compare_result(self.result)
       
        return set(self.found_items)
    
    