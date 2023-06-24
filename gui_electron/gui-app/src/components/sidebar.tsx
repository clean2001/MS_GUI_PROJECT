import React, {ReactNode, useRef, useState} from "react";
import styles from "./sidebar.module.css";
import { JsxElement } from "typescript";


type WrapperProps = {
	children: React.ReactNode;
}

function Sidebar ({children}: WrapperProps ) {
  const width = 280;
  const [isOpen, setOpen] = useState(false);
  const [xPosition, setX] = useState(width);
  const side = useRef();
  
  // button 클릭 시 토글
  const toggleMenu = () => {
    if (xPosition > 0) {
      setX(0);
      setOpen(true);
    } else {
      setX(width);
      setOpen(false);
    }
  };
  


  return (
    <div className={styles.container}>
      <div  className={styles.sidebar} style={{ width: `${width}px`, height: '100%',  transform: `translatex(${-xPosition}px)`}}>
          <button onClick={() => toggleMenu()}
          className={styles.button} >

          </button>
        
        <div className={styles.content}>{children}</div>
      </div>
    </div>
  );
};


export default Sidebar;