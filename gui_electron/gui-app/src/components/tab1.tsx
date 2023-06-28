import React, { useState } from 'react';
import styled from 'styled-components';

const TabMenu = styled.ul`
  background-color: #dcdcdc;
  font-weight: bold;
  display: flex;
  flex-direction: row;
  justify-items: center;
  align-items: center;
  list-style: none;

  .submenu {
    width:100% auto;
    padding: 15px 10px;
    cursor: pointer;
  }
`;

const Desc = styled.div`
  padding-left : 180px;
  min-height: 100vh;
  display: flex;
  
`;

export const Tab = () => {
    const [currentTab, setCurrentTab] = useState(0);
  
    const menuArr = [
      { name: 'Tab1', content: 'Tab menu ONE' },
      { name: 'Tab2', content: 'Tab menu TWO' },
      { name: 'Tab3', content: 'Tab menu THREE' },
    ];
  
    const selectMenuHandler = (index:number) => {
      setCurrentTab(index);
    };
  
    return (
      <>
        <div>
          <TabMenu>
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
  
          </TabMenu>
          <Desc>
            <h1>{menuArr[currentTab].content}</h1>
          </Desc>
        </div>
      </>
    );
};

export default Tab;