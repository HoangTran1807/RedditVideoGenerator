from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Config
screenshotDir = "Screenshots"
screenWidth = 400
screenHeight = 800

def getPostScreenshots(filePrefix, script):
    print("Taking screenshots...")
    driver, wait = __setupDriver(script.url)
    script.titleSCFile = __takeScreenshot(filePrefix, driver, wait, f"post-title-t3_{script.postId}")
    for commentFrame in script.frames:
        print(f"Taking screenshot for comment {commentFrame.commentId}")
        commentFrame.screenShotFile = __takeScreenshot(filePrefix, driver, wait, f"t1_{commentFrame.commentId}-comment-rtjson-content")
    driver.quit()

def __takeScreenshot(filePrefix, driver, wait, handle="Post"):
    # Tìm phần tử `search` bằng ID
    search = wait.until(EC.presence_of_element_located((By.ID, handle)))
    driver.execute_script("window.focus();")

    # Tìm phần tử cha của `search`
    parent_element = search.find_element(By.XPATH, '..')  # Sử dụng XPath để tìm phần tử cha
    # forcus vào phần tử cha sao cho phần tử cha nằm ở vị trí ở giữa màn hình
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", parent_element)

    # Lấy tên tệp ảnh chụp
    fileName = f"{screenshotDir}/{filePrefix}-{handle}.png"
    with open(fileName, "wb") as fp:
        fp.write(parent_element.screenshot_as_png)  # Chụp ảnh phần tử cha thay vì `search`
        
    return fileName

def __setupDriver(url: str):
    options = webdriver.ChromeOptions()
    options.headless = False
    options.add_experimental_option("mobileEmulation", {"deviceMetrics": {"width": screenWidth, "height": screenHeight, "pixelRatio": 3.0}})
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    driver.set_window_size(screenWidth, screenHeight)
    driver.get(url)

    return driver, wait
