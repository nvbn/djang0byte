# -*- coding: utf-8 -*-
import string

class _parser():
    """Parser object"""
    
    @staticmethod
    def cut(text):
        """Split text with cut"""
        if text.find('[cut]') != -1:
	    text_arr = text.split('[cut]')
	    preview = text_arr[0]
	    text = string.replace(text, '[cut]', '')
	elif text.find('[fcut]') != -1:
	    text_arr = text.split('[fcut]')
	    preview = text_arr[0]
	    text = text_arr[0]
	else:
	    preview = text
	
	return [preview, text]

    @staticmethod
    def uncut(preview, text):
        """Uncut text"""
        if text.find(preview, 0):
	    text = string.replace(text, preview, '%s[cut]' % (preview))
	elif text != preview:
	    text = '[fcut]'.join([preview, text])
	
	return text
	
    @staticmethod
    def parse(text):
        """Parse text"""
        return text
   
    @staticmethod
    def unparse(text):
        """unParse text"""
        return text
        
    
