import React, { useState } from "react";
import './tab_style.css';

function Tab() {
  const [currentTab, setCurrentTab] = useState(0);

  const menuArr = [
    { name: 'Tab1', content: 'Tab menu ONE' },
    { name: 'Tab2', content: 'Tab menu TWO' },
    { name: 'Tab3', content: 'Tab menu THREE' },
  ];

  const selectMenuHandler = (index) => {
    setCurrentTab(index);
  };

  return (
    <div>
      <ul className="TabMenu">
        {menuArr.map((ele, index)=>{
          return (
            <li
            key={index}
            className={currentTab === index ? "submenu focused" : "submenu"}
            onClick={()=> selectMenuHandler(index)}
            >
              {ele.name}
            </li>
          )
        })}
        
      </ul>

      <div className="Desc">
        <h1>{menuArr[currentTab].content}</h1>
      </div>
    </div>
  );
}