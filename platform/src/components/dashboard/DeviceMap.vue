<template>
  <div ref="mapRef" class="device-map"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import L from 'leaflet';
import type * as LType from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface DevicePoint {
  id: number|string;
  name: string;
  status: string;
  lat: number;
  lng: number;
  type?: string;
  location?: string;
}

const props = defineProps<{
  points: DevicePoint[];
  boundary?: Array<[number, number]>;
  center?: [number, number];
  zoom?: number;
  showLegend?: boolean;
}>();

const mapRef = ref<HTMLDivElement | null>(null);
let map: LType.Map | null = null;
let deviceMarkers: LType.FeatureGroup | null = null;
let boundaryLayer: LType.Polygon | null = null;

const statusStyles = {
  normal: { color: 'green', label: '正常运行' },
  warning: { color: 'orange', label: '警告状态' },
  fault: { color: 'red', label: '故障状态' },
  offline: { color: 'gray', label: '离线状态' }
};

const legendItems = [
  { status: 'normal', color: 'green', label: '正常运行' },
  { status: 'warning', color: 'orange', label: '警告状态' },
  { status: 'fault', color: 'red', label: '故障状态' },
  { status: 'offline', color: 'gray', label: '离线状态' }
];

function renderMap() {
  if (!mapRef.value) return;
  if (map) {
    map.remove();
    map = null;
  }
  map = L.map(mapRef.value).setView(props.center || [27.460, 120.381], props.zoom || 18);
  L.tileLayer('https://wprd0{s}.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scl=1&style=7', {
    subdomains: '1234',
    attribution: '高德地图',
    maxZoom: 19
  }).addTo(map);
  if (props.boundary && props.boundary.length > 2) {
    boundaryLayer = L.polygon(props.boundary, {
      color: '#1e88e5',
      weight: 2,
      opacity: 0.7,
      fillColor: '#e3f2fd',
      fillOpacity: 0.2
    }).addTo(map);
  }
  renderMarkers();
}

function renderMarkers() {
  if (!map || !props.points) return;
  if (deviceMarkers) {
    deviceMarkers.clearLayers();
    map.removeLayer(deviceMarkers);
  }
  deviceMarkers = L.featureGroup();
  props.points.forEach(device => {
    const style = statusStyles[device.status] || statusStyles.normal;
    const marker = L.circleMarker([device.lat, device.lng], {
      radius: 10,
      color: style.color,
      fillColor: style.color,
      fillOpacity: 0.85,
      weight: 2
    });
    marker.bindPopup(`
      <div style='min-width:180px;'>
        <strong>${device.name}</strong><br/>
        设备ID: ${device.id}<br/>
        状态: <span style='color:${style.color}'>${style.label}</span><br/>
        ${device.location ? `位置: ${device.location}<br/>` : ''}
        ${device.type ? `类型: ${device.type}<br/>` : ''}
        坐标: ${device.lat.toFixed(6)}, ${device.lng.toFixed(6)}
      </div>
    `);
    marker.addTo(deviceMarkers!);
  });
  deviceMarkers.addTo(map!);
  if (props.points.length > 0) {
    map!.fitBounds(deviceMarkers.getBounds(), { padding: [20, 20] });
  }
}

onMounted(() => {
  renderMap();
});
onBeforeUnmount(() => {
  if (map) {
    map.remove();
    map = null;
  }
});
watch(() => [props.points, props.boundary, props.center, props.zoom], () => {
  renderMap();
}, { deep: true });
</script>

<style scoped>
.device-map {
  width: 100%;
  height: 100%;
  min-height: 320px;
  border-radius: 14px;
}
</style> 