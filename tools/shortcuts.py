def get_module_name(model):
    mod_name =  model.__module__.lower()
    mod =  mod_name.split(".")
    if mod[0]=="apps":
        mod = mod[1]
    elif mod_name.startswith("django.contrib"):
        mod = "%s_%s" % (mod[0],mod[2])
    else:
        mod = mod[0]
    return mod
