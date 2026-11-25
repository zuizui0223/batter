// Run in a registered Google Earth Engine Code Editor session.
// Same Burns et al. 2024 product, DOI 10.3334/ORNLDAAC/2339.
// No claim of successful export until the resulting raster passes local verification.
// https://developers.google.com/earth-engine/datasets/catalog/LARSE_GEDI_GRIDDEDVEG_002_V1_1KM
var base = 'LARSE/GEDI/GRIDDEDVEG_002/V1/1KM/';
var suffix = '_vf_20190417_20230316';
var metrics = [];
for (var z=0; z<80; z+=5) metrics.push('pavd-'+z+'-'+(z+5));
metrics.push('rh-98-a0','pai-a0','cover-a0');
var region=ee.Geometry.Rectangle([-10,35,4,44], 'EPSG:4326', false);
var projection=null, stack=null;
var manifest=[];
metrics.forEach(function(metric){
  var id=base+'gediv002_'+metric+suffix;
  var raw=ee.Image(id);
  var bands=raw.bandNames().getInfo();
  if (bands.indexOf('mean')<0 || bands.indexOf('countf')<0) {
    throw Error('Missing named bands: '+id);
  }
  var a=raw.select(['mean','countf']);
  var p=a.select('mean').projection().getInfo();
  var countProjection=a.select('countf').projection().getInfo();
  if (JSON.stringify(p.transform)!==JSON.stringify(countProjection.transform) ||
      p.crs!==countProjection.crs) throw Error('Mean/count projection mismatch');
  if (projection===null) projection=p;
  else if (p.crs!==projection.crs ||
           JSON.stringify(p.transform)!==JSON.stringify(projection.transform)) {
    throw Error('Metric projection mismatch: '+metric);
  }
  // Float32 can represent the relevant shot counts exactly. Missing is -9999, not 0.
  a=a.rename([metric+'_mean',metric+'_countf']).float().unmask(-9999,false);
  stack=stack===null?a:stack.addBands(a);
  manifest.push({asset:id,bands:bands,projection:p});
});
print('Source manifest',manifest);
print('Export bands',stack.bandNames());
print('Native grid',projection);
Map.centerObject(region,6);
Map.addLayer(stack.select('pavd-0-5_mean').updateMask(stack.select('pavd-0-5_countf').gte(10)),
             {min:0,max:0.5,palette:['ffffff','6fae76','144c27']},'0-5 m PAVD; >=10 shots');
Export.image.toDrive({
  image:stack,description:'GEDI_Iberia_1km_16strata_20190417_20230316',
  folder:'batter_gedi',fileNamePrefix:'gedi_iberia_native',
  region:region,crs:projection.crs,crsTransform:projection.transform,
  maxPixels:1e8,fileFormat:'GeoTIFF',formatOptions:{cloudOptimized:true,noData:-9999}
});
