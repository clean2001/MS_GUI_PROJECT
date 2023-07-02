import React, { useState, useEffect } from 'react';

function showGraph(terminal) {
  let tmp = document.querySelector('#graph-iframe');
  console.log(terminal);
  tmp.src = `${terminal}`;
}


function Sidebar(props) {
  const [ spectrumIdx, setSpectrumIdx ] = useState(0); 

  const [NisPushed, setNPushed] = useState(false);
  const [CisPushed, setCPushed] = useState(false);
  let terminal;

  useEffect(()=>{
      checkStates();
  }, [NisPushed, CisPushed, spectrumIdx]);

  function checkStates() {
      let terminal;
      if(NisPushed === true && CisPushed === true) {
          terminal = './spectrums/spectrum_ncterm'+spectrumIdx+'.html';
      } else if(NisPushed === true && CisPushed == false) { // N만 눌린 상태
          terminal = './spectrums/spectrum_nterm'+spectrumIdx+'.html';
      } else if(CisPushed === true && NisPushed === false) {
          terminal = './spectrums/spectrum_cterm'+spectrumIdx+'.html';
      } else if(CisPushed === false && NisPushed === false){
          terminal = './spectrums/spectrum_naive'+spectrumIdx+'.html';
      }

      showGraph(terminal);
  } 
  
  function toggleNBtn() {
      setNPushed(!NisPushed);

  }

  function toggleCBtn() {
      setCPushed(!CisPushed);
  }


  function reShowGraph(idx, title, seq, terminal) {

      let spectrum_title = document.querySelector('#spectrum_title');
      let spectrum_seq = document.querySelector('#spectrum_seq');
      spectrum_title.innerHTML = `${title}`;
      spectrum_seq.innerHTML = `${seq}`;
      if(spectrumIdx === idx) return;

  
      setSpectrumIdx(idx);
  
      showGraph(terminal)
  }
  
  
  const spectrum_list = props.data.map((obj) => 
          <p key={obj.title}
          className={obj.idx===spectrumIdx? 'current-spectrum' : 'not-current'}
          onClick={() => reShowGraph(obj.idx, obj.title, obj.seq)}>{obj.title}</p>
  );

  return (
    <ul className="sidebar">
      {spectrum_list}
    </ul>
  );
}
