# defining "mouse" product
product mouse { 
    name: 'Optical Mouse'; 
    description: 'Mouse with optical technology'; 
    category: 'Accessories'; 
    price: 29.99; 
    quantity: 100; 
}

# defining "monitor" product
product monitor { 
    name: 'Monitor'; 
    description: ''; 
    category: 'Accessories'; 
    price: 99.99; 
    quantity: 30; 
}

# defining "keyboard" product
product keyboard { 
    name: 'Keyboard'; 
    description: ''; 
    category: 'Accessories'; 
    price: 49.99; 
    quantity: 53; 
}

monthly_mouse_inflow = 10;
monthly_mouse_outflow = 5;

print("initial mouse price = " + mouse.price);
print("initial mouse quantity = " + mouse.quantity);
print("initial monitor quantity = " + monitor.quantity);
print("initial keyboard quantity = " + keyboard.quantity);
print("");
print("monthly_mouse mouse in flow: " + monthly_mouse_inflow);
print("monthly_mouse mouse out flow: " + monthly_mouse_outflow);
print("");

in mouse monthly_mouse_inflow;
out mouse monthly_mouse_outflow;
mouse.price = 25.50;

print("mouse price = " + mouse.price);
print("mouse quantity = " + mouse.quantity);
print("");
print("type of in flow: " + monthly_mouse_inflow.type);
print("");

function peripherals_combo_promotion():
    print("combo promotion!");
    out monitor 1;
    out keyboard 1;
    out mouse 1;
    end;

peripherals_combo_promotion();

print("final mouse quantity = " + mouse.quantity);
print("final monitor quantity = " + monitor.quantity);
print("final keyboard quantity = " + keyboard.quantity);

rm mouse;
rm monitor;
rm keyboard;