d3.json('/data', response => {
  console.log('count: ', response.count);
  d3.select('#studentCount').text(response.count);
});
