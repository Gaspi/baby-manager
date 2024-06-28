function get(id) { return document.getElementById(id); }
const logdiv = get("logs");
const timeline = get('timeline');
const fileInput = get('file-input');

var babydata;


function log(msg) {
  const newlog = document.createElement("p");
  newlog.innerText = msg;
  logdiv.appendChild(newlog);
}

function load(data) {
  if (data && data.zip) {
    try {
      // Creates a BlobReader object used to read `zipFileBlob`.
      const zipFileReader = new zip.BlobReader(data.zip);
      // Creates a TextWriter object where the content of the first entry in the zip will be written.
      const helloWorldWriter = new zip.TextWriter();
      // Creates a ZipReader object reading the zip content via `zipFileReader`,
      // retrieves metadata (name, dates, etc.) of the first entry, retrieves its
      // content via `helloWorldWriter`, and closes the reader.
      const zipReader = new zip.ZipReader(zipFileReader);
      const entries = zipReader.getEntries().then( (entries) => {
        entries.shift().getData(helloWorldWriter).then( (txt) => {
          zipReader.close();
          babydata = JSON.parse(txt);
          preprocess(babydata);
          fileInput.style.display = 'none';
          get('title').style.display = 'none';
          get('logs').style.display = 'none';
          show(babydata);
          log(`Unzipping successful!`);
          });
      });
    } catch (e) {
      log(`Error while unzipping: ${e}`);
    }
  }
}

function getDatePart(date) {
  return new Date(date.toDateString());
}

function getTimeOfDay(date) {
  const res = new Date(date);
  res.setFullYear(2000);
  res.setMonth(0);
  res.setDate(1);
  return res;
}

function formatDate(d) {
  return d.toLocaleDateString('fr-FR', {weekday:"short", day:"2-digit", month:"2-digit"});
}

function formatDateTime(d) {
  return d.toLocaleString('fr-FR', {weekday:"long", day:"2-digit", month:"2-digit", hour:"2-digit", minute:"2-digit"});
}

function formatTime(d) {
  return new Date(d).toLocaleTimeString('fr-FR', {hour:"2-digit", minute:"2-digit"});
}


function preprocess(data) {
  data.baby_sleep.forEach((d)=> {
    d.startDate = new Date(d.startDate);
    d.startDay = getDatePart(d.startDate);
    d.startTime = getTimeOfDay(d.startDate);

    d.endDate = new Date(d.endDate);
    if (d.endDate.getTime() === 0) { d.endDate = new Date(); }
    d.endDay = getDatePart(d.endDate);
    d.endTime = getTimeOfDay(d.endDate);

    const duration = d.endDate-d.startDate;
    d.duration = new Date( new Date(2000,0,1).getTime()+duration );
    d.overnight = (d.startDay.getTime() !== d.endDay.getTime());
  });

  data.baby_nursingfeed.forEach((d)=> {
    d.startDate = new Date(d.startDate);
    d.startDay = getDatePart(d.startDate);
    d.startTime = getTimeOfDay(d.startDate);

    d.endDate = new Date(d.endDate);
    if (d.endDate.getTime() === 0) { d.endDate = new Date(); }
    d.endDay = getDatePart(d.endDate);
    d.endTime = getTimeOfDay(d.endDate);

    const duration = d.endDate-d.startDate;
    d.duration = new Date( new Date(2000,0,1).getTime()+duration );
    d.overnight = (d.startDay.getTime() !== d.endDay.getTime());
  });

  data.baby_nappy.forEach((d) => {
    d.date = new Date(d.date);
    d.day = getDatePart(d.date);
    d.time = getTimeOfDay(d.date);
    d.label = formatDate(d.day);
  });
  data.baby_bottlefeed.forEach((d) => {
    d.date = new Date(d.date);
    d.day = getDatePart(d.date);
    d.time = getTimeOfDay(d.date);
    d.label = formatDate(d.day);
  });

  data.firstSleepDay = new Date( Math.min(...data.baby_sleep.map((d)=>d.startDay)) );
  data.lastSleepDay = new Date( Math.max(...data.baby_sleep.map((d)=>d.endDay)) );
  data.allSleepLabels = [];
  const cur = new Date(data.firstSleepDay);
  while (cur.getTime() <= data.lastSleepDay.getTime()) {
    data.allSleepLabels.push(formatDate(cur));
    cur.setDate(cur.getDate() + 1);
  }
  get('chart').style.height = (45*data.allSleepLabels.length)+"px"

  data.baby_sleep_graph = [];
  data.baby_sleep.forEach((d)=> {
    if (d.overnight) {
      data.baby_sleep_graph.push({
        label: formatDate(d.startDay),
        range: [d.startTime, new Date(2000,0,2)],
        d: d
      });
      data.baby_sleep_graph.push({
        label: formatDate(d.endDay),
        range: [new Date(2000,0,1), d.endTime],
        d: d
      });
    } else {
      data.baby_sleep_graph.push({
        label: formatDate(d.startDay),
        range: [d.startTime, d.endTime],
        d: d
      });
    }
  });

  data.baby_nursingfeed_graph = [];
  data.baby_nursingfeed.forEach((d)=> {
    if (d.overnight) {
      data.baby_nursingfeed_graph.push({
        label: formatDate(d.startDay),
        range: [d.startTime, new Date(2000,0,2)],
        d: d
      });
      data.baby_nursingfeed_graph.push({
        label: formatDate(d.endDay),
        range: [new Date(2000,0,1), d.endTime],
        d: d
      });
    } else {
      data.baby_nursingfeed_graph.push({
        label: formatDate(d.startDay),
        range: [d.startTime, d.endTime],
        d: d
      });
    }
  });
}

function label(d) {
  if (d.dataset.label === "Dodo") {
    const start = formatTime(d.raw.d.startTime);
    const end = formatTime(d.raw.d.endTime);
    const duration = d.raw.d.duration.toLocaleTimeString('fr-FR', {hour:"2-digit", minute:"2-digit"});
    return `${start} - ${end} (${duration})`;
  } else if (d.dataset.label === "Sein") {
    const start = formatTime(d.raw.d.startTime);
    const end = formatTime(d.raw.d.endTime);
    const duration = d.raw.d.duration.toLocaleTimeString('fr-FR', {hour:"2-digit", minute:"2-digit"});
    return `${start} - ${end} (${duration})`;
  } else if (d.dataset.label === "Couche") {
    return formatTime(d.raw.time);
  } else if (d.dataset.label === "Biberon") {
    return `${formatTime(d.raw.time)} : ${d.raw.amountML}ml`;
  }
}

function show(data) {
  const myChart = new Chart(get('chart'), {
//      type: 'bar',
      data: {
        labels: data.allSleepLabels,
        datasets: [
            {
              type: "bar",
              label: "Dodo",
              data: data.baby_sleep_graph,
              backgroundColor: "#36a2eb",
              parsing: {
                xAxisKey: 'range',
                yAxisKey: 'label'
              },
              order: 3,
            },
            {
              type: "bar",
              label: "Sein",
              data: data.baby_nursingfeed_graph,
              backgroundColor: "#ff9f40",
              parsing: {
                xAxisKey: 'range',
                yAxisKey: 'label'
              },
              order: 2,
            },
            {
              type: "scatter",
              label: "Couche",
              data: data.baby_nappy,
              parsing: {
                xAxisKey: 'time',
                yAxisKey: 'label'
              },
              order: 1,
              radius: 6,
              pointHoverRadius: 6,
              backgroundColor:"#F1948A",
              pointHoverBackgroundColor: 'red',
              borderColor: '#E74C3C',
              borderWidth: 2,
            },
            {
              type: "scatter",
              label: "Biberon",
              data: data.baby_bottlefeed,
              radius: 8,
              pointHoverRadius: 8,
              pointHoverBackgroundColor: 'red',
              backgroundColor: '#F8C471',
              borderColor: '#F39C12',
              borderWidth: 2,
              parsing: {
                xAxisKey: 'time',
                yAxisKey: 'label'
              },
              order: 1,
            }
          ]
    },
    options: {
      responsive: false,
      animation: false,
      indexAxis: 'y',
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: 'Le planning de Sacha'
        },
        tooltip: {
          callbacks: { label: label }
        },
      },
      scales: {
        y: {
          stacked: true,
          ticks: {
            callback: function(value, index, ticks) {
              const label = this.getLabelForValue(value);
              const s = label.split('.', 2);
              return [ s[0], s[1].substring(1)];
            }
          }
        },
        x: {
          type: 'time',
          //stacked: true,
          time: { tooltipFormat: 'dd' }, // Luxon format string
          min: new Date(2000,0,1),
          max: new Date(2000,0,2),
          ticks: {
            callback: formatTime,
            stepSize: 60,
            autoSkip: false
          }
        }
      }
    }
  });
}


fileInput.onchange = (e) => load({zip: e.target.files[0]});

window.onload = function() {
  const xhttp = new XMLHttpRequest();
  xhttp.responseType = 'blob';
  xhttp.onload = (e) => load({zip: e.currentTarget.response});
  xhttp.open("GET", "../babyplus_data_export.zip");
  xhttp.send();
}

if ("serviceWorker" in navigator) {
  // register service worker
  navigator.serviceWorker.register("service-worker.js")
    .then(registration => {
      console.log('Service Worker registered with scope:', registration.scope);
    })
    .catch(error => {
      console.error('Service Worker registration failed:', error);
    });
  navigator.serviceWorker.addEventListener('message',  (event) => { load(event.data); });
}

