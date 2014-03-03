/*These lines are all chart setup.  Pick and choose which chart features you want to utilize. */

$(document).ready(function(){
    $(".chart-panel").each(function(){
        var that = this;
        nv.addGraph(function() {
            var chart = nv.models.lineChart()
                    .margin({left: 100})  //Adjust chart margins to give the x-axis some breathing room.
                    .useInteractiveGuideline(true)  //We want nice looking tooltips and a guideline!
                    .transitionDuration(350)  //how fast do you want the lines to transition?
                ;

            chart.xAxis.axisLabel('Date').tickFormat(function(d) {
                return d3.time.format("%Y-%m-%d")(new Date(d * 1000))
            });

            chart.yAxis     //Chart y-axis settings
                .axisLabel('Value')
                .tickFormat(d3.format('.01f'));

            var input = $(".chart-data", that);
            var x = input.data("x");
            var y = input.data("y");

            var newData = [];
            for(var i=0;i< x.length;i++){
                newData.push({x: parseFloat(x[i]), y: parseFloat(y[i])})
            }

            var chartData = [
                {
                    values: newData,      //values - represents the array of {x,y} data points
                    key: 'Metric' //key  - the name of the series.
                },
            ];
            d3.select($(that).find(".chart svg")[0])    //Select the <svg> element you want to render the chart in.
                .datum(chartData)         //Populate the <svg> element with chart data...
                .call(chart);          //Finally, render the chart!

            //Update the chart when window resizes.
            nv.utils.windowResize(function() { chart.update() });
            return chart;
        });
    });
});