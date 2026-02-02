def is_dynamic_site(url):
    dynamic_sites = ["amazon", "flipkart", "myntra", "meesho"]
    return any(site in url.lower() for site in dynamic_sites)
