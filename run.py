from main.scrape import Scrape


inst = Scrape()
inst.land_on_first_page()
inst.select_contry()
inst.get_states()
state = input("Enter the value of state from above list: ")
inst.input_state(state=state)
inst.select_date()
while True:
    date_from= input("Enter the date from in format mm/dd/yyyy: ")
    date_to= input("Enter the date to in format mm/dd/yyyy: ")
    inst.date_range(date_from=date_from,date_to=date_to)
    inst.search()
    result_cond = inst.get_result()
    print(result_cond)
    if result_cond == False:
        break
    print("Result Exceeded from limit \n please enter ad valid date range")
inst.scrolldown()
inst.result_to_csv()
inst.runscrapper()
print("Result got")