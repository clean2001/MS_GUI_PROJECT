import React, { useState } from 'react';

const [activeIndex, setActiveIndex] = useState(0);

const tabContArr = [
    {
        tabTitle:(
            <li className={activeIndex===0 ? "is-active" : ""} onClick={()=>tabClickHandler(0)}>
                탭1
            </li>
        ),
        tabCont:(
            <div>탭1 내용</div>
        )
    },
    {
        tabTitle:(
            <li className={activeIndex===1 ? "is-active" : ""} onClick={()=>tabClickHandler(1)}>
                탭2
            </li>
        ),
        tabCont:(
            <div>탭2 내용</div>
        )
    }
];

const tabClickHandler=(index:number)=>{
    setActiveIndex(index)
}

export const TabMenu = () => {
    return (
        <ul className="tabs is-boxed">
            {tabContArr.map((section, index)=>{
                return section.tabTitle
            })}
            <div>
                { tabContArr[activeIndex].tabCont }
            </div>
        </ul>
    );

}

export default TabMenu;