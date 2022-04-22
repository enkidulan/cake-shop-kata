*** Settings ***
Library    python_zca_cakes
Library    helpers.py
Suite Setup    Bootstrap Cake Shop


*** Test Cases ***
The delivery date for a cake is the order date plus the lead time
    When an order for a 2-day lead-time cake placed on Monday afternoon
    Then the order has a delivery date of Wednesday

Small cakes have a lead time of 2 days
    When an order for a small cake placed on Monday afternoon
    Then the order has a delivery date of Wednesday

Big cakes have a lead time of 3 days
    When an order for a big cake placed on Monday afternoon
    Then the order has a delivery date of Thursday

If a cake order is received in the morning (ie, before 12pm) then baking starts on the same day
    When an order for a small cake placed on Monday morning
    Then the order has a delivery date of Tuesday

Custom frosting adds 2 days extra lead time, you can only frost a baked cake
    When an order for a small cake placed on Monday morning
    And the cake should have custom frosting
    Then the order has a delivery date of Thursday
    And Marco bakes the cake Monday,Tuesday
    And Sandro frosts the cake Wednesday,Thursday


*** Test Cases ***
Marco only works Monday-Friday (small cake)
    When an order for a small cake placed on Friday morning
    Then the order has a delivery date of Monday

Marco only works Monday-Friday (small cake with frosting)
    When an order for a small cake placed on Friday morning
    And the cake should have custom frosting
    Then the order has a delivery date of Wednesday

Sandro works Tuesday-Saturday
    When an order for a big cake placed on Tuesday afternoon
    And the cake should have custom frosting
    Then the order has a delivery date of next-Tuesday
    And Marco bakes the cake Wednesday,Thursday,Friday
    And Sandro frosts the cake Saturday,next-Tuesday


*** Test Cases ***
Fancy boxes have a lead time of 3 days
    When an order for a small cake placed on Monday morning
    And the cake should arrive in a fancy box
    Then the order has a delivery date of Wednesday
    And Marco bakes the cake Monday,Tuesday
    And the box arrives Wednesday

Fancy boxes do not affect delivery time for big cakes
    When An order for a big cake placed on Monday morning
    And the cake should arrive in a fancy box
    Then the order has a delivery date of Wednesday
    and Marco bakes the cake Monday,Tuesday,Wednesday
    The box arrives Wednesday

Boxes can be ordered from the supplier before cakes are finished
    When an order for a big cake placed on Monday afternoon
    And the cake should arrive in a fancy box
    Then the order has a delivery date of Thursday
    And Marco bakes the cake Tuesday,Wednesday,Thursday
    And the box arrives Wednesday


*** Test Cases ***

Sandro is allergic to nuts so Marco handles nuts-adding instead
    When an order for a small cake placed on Monday morning
    And the cake should be decorated with nuts
    Then the order has a delivery date of Wednesday
    And Marco bakes the cake Monday,Tuesday
    And Marco adds nuts on Wednesday

Decorating a cake with nuts takes 1 day
    When an order for a small cake placed on Monday morning
    And the cake should have custom frosting
    And the cake should be decorated with nuts
    Then the order has a delivery date of Friday
    And Marco bakes the cake Monday,Tuesday
    And Sandro frosts the cake Wednesday,Thursday
    And Marco adds nuts on Friday

Nuts can only be added after frosting, as nobody wants frosty nuts
    When an order for a small cake placed on Tuesday morning
    And the cake should have custom frosting
    And the cake should be decorated with nuts
    And the cake should arrive in a fancy box
    Then the order has a delivery date of Monday
    And Marco bakes the cake Tuesday,Wednesday
    And Sandro frosts the cake Thursday,Friday
    And the box arrives Thursday
    And Marco adds nuts on Monday

*** Test Cases ***
Cakes that will not be complete before 23rd of December will be unable to start production until 2nd of January
    When an order for a small cake placed on 22 December 2022
    Then the order has a delivery date of 3 January 2023
    And Marco bakes the cake 2 January 2023, 3 January 2023

The shop closes for Christmas from the 23rd of December and is open again on the 2nd of January that coincide with Sunday, so Marco doesn't start the cake until onday 3rd
    When an order for a small cake placed on 22 December 2021
    Then the order has a delivery date of 4 January 2022

The shop closes for Christmas from the 23rd of December, but deliveres cakes on 22nd of December
    When an order for a small cake placed on morning 21 December 2021
    Then the order has a delivery date of 22 December 2021

Fancy boxes will continue to arrive throughout the festive period
    When an order for a small cake placed on 22 December 2022
    And the cake should arrive in a fancy box
    Then the order has a delivery date of 3 January 2023
    And Marco bakes the cake 2 January 2023, 3 January 2023
    And the box arrives 24 December 2022

A cake won't be baked until box arrives
    When an order for a small cake placed on 21 December 2022
    And the cake should arrive in a fancy box
    and Marco could bake cakes on the December 21 and 22
    Then the order has a delivery date of 3 January 2023
    And the box arrives 23 December 2022
    And Marco bakes the cake 2 January 2023, 3 January 2023


*** Keywords ***
an order for a ${size} cake placed on ${day}
    ${normalized_day}=   Convert To Date     ${day}
    ${size} =    Evaluate    'big' if '${size}' == 'big' else 'small'
    ${cake_order} =   Place Cake Order   cake_size=${size}   order_time=${normalized_day}
    Set Test Variable  ${cake_order}
the cake should have custom frosting
    ${cake_order.add_frosting} =    Set Variable    True
the cake should be decorated with nuts
    ${cake_order.add_nuts} =    Set Variable    True
the cake should arrive in a fancy box
    ${cake_order.add_fancy_box} =    Set Variable    True
the order has a delivery date of ${day}
    ${normalized_day}=   Convert To Date     ${day}    ${cake_order.order_time}
    ${delivery_date}=    Calculate Delivery Date       ${cake_order}
    Should Be Equal
    ...  ${delivery_date.strftime('%Y-%m-%d %a')}
    ...  ${normalized_day.strftime('%Y-%m-%d %a')}
    ...  ${cake_order} has ${delivery_date.strftime('%Y-%m-%d %a')} delivery date instead of expected ${normalized_day.strftime('%Y-%m-%d %a')}
And ${person} ${action} the cake ${days}
    FOR    ${day}    IN    @{days.split(',')}
        ${normalized_day}=    Convert To Date     ${day}    ${cake_order.order_time}
        Should Be True   ['${person}', '${action}', '${normalized_day.strftime('%Y-%m-%d')}'] in ${cake_order.baking_schedule}
    END
and Marco could bake cakes on the December 21 and 22
    LOG   Marco could bake the cake on the
the box arrives ${day}
    ${normalized_day}=    Convert To Date     ${day}    ${cake_order.order_time}
    Should Be True   ['box arrives', '${normalized_day.strftime('%Y-%m-%d')}'] in ${cake_order.baking_schedule}
And ${person} adds nuts on ${day}
    ${normalized_day}=    Convert To Date     ${day}    ${cake_order.order_time}
    Should Be True   ['${person}', 'adds nuts', '${normalized_day.strftime('%Y-%m-%d')}'] in ${cake_order.baking_schedule}
${person} comes back from holiday ${day}
    Should Be Equal     ${day}   1
${person} could bake the cake on ${day}
    Should Be Equal     ${day}   1
${person} waits for the box to arrive before star baking
    Should Be Equal     1   0

