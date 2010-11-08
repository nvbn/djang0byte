def file_upload_path(instance, filename):
    """Generates upload path
    
    Keyword arguments:
    instance -- FileField
    filename - String
    
    Returns: String
    
    """
    parts = filename.rsplit('.', 1)
    str = "%s.%s" % (slugify(translify(parts[0])), slugify(translify(parts[1])))
    return "%s/%s/%s/%s" % (strftime('%Y'), 
       strftime('%m'), strftime('%d'), str)
