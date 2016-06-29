from selenium import webdriver

driver = webdriver.PhantomJS() # or add to your PATH
# driver.set_window_size(1024, 768) # optional
# driver.get('https://google.com/')
# driver.set_preference( "network.proxy.socks_version", 5 )
# driver.set_preference( "network.proxy.socks", '127.0.0.1' )
# driver.set_preference( "network.proxy.socks_port", 9050 )
print dir(driver)
driver.save_screenshot('screen.png') # save a screenshot to disk
# sbtn = driver.find_element_by_css_selector('button.gbqfba')
# sbtn.click()