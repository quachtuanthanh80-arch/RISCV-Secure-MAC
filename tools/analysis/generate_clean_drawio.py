import xml.etree.ElementTree as ET
from pathlib import Path

def generate_fig1_xml():
    xml = '''<mxfile host="app.diagrams.net" agent="Antigravity" version="24.0.0">
  <diagram id="fig1_rv32i_original" name="RV32I_5Stage_Original">
    <mxGraphModel dx="1800" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="2000" pageHeight="1100" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- Title -->
        <mxCell id="title" parent="1" style="text;html=1;align=center;verticalAlign=middle;resizable=0;points=[];autosize=1;strokeColor=none;fillColor=none;fontSize=22;fontStyle=1;fontColor=#0F172A;" value="SƠ ĐỒ ĐƯỜNG TRUYỀN DỮ LIỆU RV32I 5 TẦNG PIPELINE VÀ GHÉP NỐI NGOẠI VI MMIO" vertex="1">
          <mxGeometry x="250" y="20" width="1500" height="40" as="geometry" />
        </mxCell>

        <!-- STAGE BACKGROUNDS (Dashed Containers) -->
        <!-- Stage 1 IF -->
        <mxCell id="bg_if" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F0FDF4;strokeColor=#16A34A;strokeWidth=2;dashed=1;verticalAlign=top;fontSize=15;fontStyle=1;fontColor=#15803D;spacingTop=12;" value="IF (Instruction Fetch)" vertex="1">
          <mxGeometry x="40" y="90" width="340" height="740" as="geometry" />
        </mxCell>
        <!-- Stage 2 ID -->
        <mxCell id="bg_id" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F0F9FF;strokeColor=#0284C7;strokeWidth=2;dashed=1;verticalAlign=top;fontSize=15;fontStyle=1;fontColor=#0369A1;spacingTop=12;" value="ID (Instruction Decode)" vertex="1">
          <mxGeometry x="390" y="90" width="320" height="740" as="geometry" />
        </mxCell>
        <!-- Stage 3 EX -->
        <mxCell id="bg_ex" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF7ED;strokeColor=#EA580C;strokeWidth=2;dashed=1;verticalAlign=top;fontSize=15;fontStyle=1;fontColor=#C2410C;spacingTop=12;" value="EX (Execution)" vertex="1">
          <mxGeometry x="720" y="90" width="310" height="740" as="geometry" />
        </mxCell>
        <!-- Stage 4 MEM -->
        <mxCell id="bg_mem" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FAF5FF;strokeColor=#9333EA;strokeWidth=2;dashed=1;verticalAlign=top;fontSize=15;fontStyle=1;fontColor=#7E22CE;spacingTop=12;" value="MEM (Memory Access)" vertex="1">
          <mxGeometry x="1040" y="90" width="310" height="740" as="geometry" />
        </mxCell>
        <!-- Stage 5 WB -->
        <mxCell id="bg_wb" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF1F2;strokeColor=#E11D48;strokeWidth=2;dashed=1;verticalAlign=top;fontSize=15;fontStyle=1;fontColor=#BE185D;spacingTop=12;" value="WB (Write Back)" vertex="1">
          <mxGeometry x="1360" y="90" width="310" height="740" as="geometry" />
        </mxCell>

        <!-- PIPELINE DIVIDERS (Vertical Dashed Lines) -->
        <mxCell id="div_if_id" parent="1" style="edgeStyle=none;html=1;dashed=1;strokeColor=#16A34A;strokeWidth=2;endArrow=none;" edge="1">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="385" y="90" as="sourcePoint" />
            <mxPoint x="385" y="830" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="div_id_ex" parent="1" style="edgeStyle=none;html=1;dashed=1;strokeColor=#0284C7;strokeWidth=2;endArrow=none;" edge="1">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="715" y="90" as="sourcePoint" />
            <mxPoint x="715" y="830" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="div_ex_mem" parent="1" style="edgeStyle=none;html=1;dashed=1;strokeColor=#EA580C;strokeWidth=2;endArrow=none;" edge="1">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="1035" y="90" as="sourcePoint" />
            <mxPoint x="1035" y="830" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="div_mem_wb" parent="1" style="edgeStyle=none;html=1;dashed=1;strokeColor=#9333EA;strokeWidth=2;endArrow=none;" edge="1">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="1355" y="90" as="sourcePoint" />
            <mxPoint x="1355" y="830" as="targetPoint" />
          </mxGeometry>
        </mxCell>

        <!-- STAGE 1 (IF) COMPONENTS -->
        <mxCell id="pc_reg" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#16A34A;strokeWidth=2;fontSize=14;fontColor=#0F172A;" value="&lt;b&gt;&lt;font style=&quot;font-size: 16px; color: #15803D;&quot;&gt;PC&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;br&gt;32-bit Reg" vertex="1">
          <mxGeometry x="65" y="340" width="125" height="160" as="geometry" />
        </mxCell>
        <mxCell id="pc_adder" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#16A34A;strokeWidth=2;fontSize=14;fontColor=#0F172A;" value="&lt;b&gt;&lt;font style=&quot;font-size: 16px; color: #15803D;&quot;&gt;+4&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;br&gt;PC Adder" vertex="1">
          <mxGeometry x="215" y="180" width="130" height="100" as="geometry" />
        </mxCell>
        <mxCell id="imem" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#16A34A;strokeWidth=2;fontSize=14;fontColor=#0F172A;" value="&lt;b&gt;&lt;font style=&quot;font-size: 16px; color: #15803D;&quot;&gt;IMEM&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;br&gt;ROM 64x32" vertex="1">
          <mxGeometry x="215" y="320" width="130" height="200" as="geometry" />
        </mxCell>

        <!-- STAGE 2 (ID) COMPONENTS -->
        <mxCell id="regfile" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0284C7;strokeWidth=2;fontSize=14;fontColor=#0F172A;" value="&lt;b&gt;&lt;font style=&quot;font-size: 16px; color: #0369A1;&quot;&gt;Register File&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;br&gt;32 x 32b (1024 FFs)&lt;br&gt;2 Read, 1 Write Port" vertex="1">
          <mxGeometry x="420" y="280" width="260" height="290" as="geometry" />
        </mxCell>
        <mxCell id="imm_gen" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0284C7;strokeWidth=2;fontSize=14;fontColor=#0F172A;" value="&lt;b&gt;Imm Gen&lt;/b&gt;&lt;br&gt;&lt;br&gt;6 Formats&lt;br&gt;(I, S, B, U, J)" vertex="1">
          <mxGeometry x="420" y="640" width="125" height="160" as="geometry" />
        </mxCell>
        <mxCell id="ctrl_unit" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0284C7;strokeWidth=2;fontSize=14;fontColor=#0F172A;" value="&lt;b&gt;Control&lt;/b&gt;&lt;br&gt;&lt;br&gt;Unit&lt;br&gt;Decoder" vertex="1">
          <mxGeometry x="555" y="640" width="125" height="160" as="geometry" />
        </mxCell>

        <!-- STAGE 3 (EX) COMPONENTS -->
        <mxCell id="alu" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#EA580C;strokeWidth=2;fontSize=14;fontColor=#0F172A;" value="&lt;b&gt;&lt;font style=&quot;font-size: 16px; color: #C2410C;&quot;&gt;32-bit ALU&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;br&gt;10 Operations&lt;br&gt;(ADD, SUB, SLL, XOR...)" vertex="1">
          <mxGeometry x="745" y="300" width="260" height="270" as="geometry" />
        </mxCell>
        <mxCell id="branch_cmp" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#EA580C;strokeWidth=2;fontSize=14;fontColor=#0F172A;" value="&lt;b&gt;&lt;font style=&quot;font-size: 16px; color: #C2410C;&quot;&gt;Branch Cmp&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;br&gt;BEQ, BNE, BLT, BGE&lt;br&gt;Zero Delay Logic" vertex="1">
          <mxGeometry x="745" y="640" width="260" height="160" as="geometry" />
        </mxCell>

        <!-- STAGE 4 (MEM) COMPONENTS -->
        <mxCell id="dmem" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#9333EA;strokeWidth=2;fontSize=14;fontColor=#0F172A;" value="&lt;b&gt;&lt;font style=&quot;font-size: 16px; color: #7E22CE;&quot;&gt;Data RAM&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;br&gt;dmem.sv (32 RAMS64E)&lt;br&gt;0x0000..0x0FFF" vertex="1">
          <mxGeometry x="1065" y="300" width="260" height="230" as="geometry" />
        </mxCell>
        <mxCell id="mmio_bus" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F3E8FF;strokeColor=#9333EA;strokeWidth=2;fontSize=13;fontColor=#0F172A;" value="&lt;b&gt;&lt;font style=&quot;font-size: 15px; color: #7E22CE;&quot;&gt;MMIO Bus MUX&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;br&gt;0x8000_0000 (A)&lt;br&gt;0x8000_0004 (B)&lt;br&gt;0x8000_0008 (C/Start)&lt;br&gt;0x8000_000C (Out)" vertex="1">
          <mxGeometry x="1065" y="580" width="260" height="230" as="geometry" />
        </mxCell>

        <!-- STAGE 5 (WB) COMPONENTS -->
        <mxCell id="wb_mux" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#E11D48;strokeWidth=2;fontSize=14;fontColor=#0F172A;" value="&lt;b&gt;&lt;font style=&quot;font-size: 16px; color: #BE185D;&quot;&gt;WB MUX&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;br&gt;&lt;font style=&quot;font-size: 13px;&quot;&gt;ALU_out&lt;br&gt;Mem_out&lt;br&gt;PC + 4&lt;br&gt;MAC_out&lt;/font&gt;" vertex="1">
          <mxGeometry x="1390" y="290" width="190" height="300" as="geometry" />
        </mxCell>

        <!-- HAZARD & FORWARDING UNIT (BOTTOM) -->
        <mxCell id="hazard_unit" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#DC2626;strokeWidth=2;fontSize=14;fontColor=#0F172A;" value="&lt;b&gt;&lt;font style=&quot;font-size: 16px; color: #991B1B;&quot;&gt;Hazard Unit &amp; Data Forwarding Unit&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 13px;&quot;&gt;Resolves Load-Use Stall (1 Bubble) + EX/MEM &amp; MEM/WB Data Bypassing&lt;/font&gt;" vertex="1">
          <mxGeometry x="420" y="860" width="955" height="70" as="geometry" />
        </mxCell>

        <!-- SIGNAL BADGES -->
        <mxCell id="badge_next_pc" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#16A34A;strokeWidth=1.5;fontSize=12;fontStyle=1;fontColor=#16A34A;" value="Next PC" vertex="1">
          <mxGeometry x="345" y="140" width="65" height="25" as="geometry" />
        </mxCell>
        <mxCell id="badge_instr" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0284C7;strokeWidth=1.5;fontSize=12;fontStyle=1;fontColor=#0284C7;" value="Instr [31:0]" vertex="1">
          <mxGeometry x="340" y="405" width="85" height="25" as="geometry" />
        </mxCell>
        <mxCell id="badge_rs1" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#EA580C;strokeWidth=1.5;fontSize=12;fontStyle=1;fontColor=#EA580C;" value="rs1_data" vertex="1">
          <mxGeometry x="675" y="365" width="65" height="25" as="geometry" />
        </mxCell>
        <mxCell id="badge_rs2" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#EA580C;strokeWidth=1.5;fontSize=12;fontStyle=1;fontColor=#EA580C;" value="rs2_data" vertex="1">
          <mxGeometry x="675" y="520" width="65" height="25" as="geometry" />
        </mxCell>
        <mxCell id="badge_alu_out" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#9333EA;strokeWidth=1.5;fontSize=12;fontStyle=1;fontColor=#9333EA;" value="ALU_out" vertex="1">
          <mxGeometry x="1000" y="420" width="65" height="25" as="geometry" />
        </mxCell>
        <mxCell id="badge_mmio_addr" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#9333EA;strokeWidth=1.5;fontSize=12;fontStyle=1;fontColor=#9333EA;" value="MMIO Addr" vertex="1">
          <mxGeometry x="990" y="570" width="80" height="25" as="geometry" />
        </mxCell>
        <mxCell id="badge_mem_data" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#E11D48;strokeWidth=1.5;fontSize=12;fontStyle=1;fontColor=#E11D48;" value="Mem_data" vertex="1">
          <mxGeometry x="1320" y="415" width="75" height="25" as="geometry" />
        </mxCell>
        <mxCell id="badge_mac_out" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#E11D48;strokeWidth=1.5;fontSize=12;fontStyle=1;fontColor=#E11D48;" value="MAC_out" vertex="1">
          <mxGeometry x="1315" y="700" width="70" height="25" as="geometry" />
        </mxCell>
        <mxCell id="badge_wb" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#E11D48;strokeWidth=1.5;fontSize=13;fontStyle=1;fontColor=#E11D48;" value="WriteBack Data [31:0]" vertex="1">
          <mxGeometry x="1560" y="235" width="165" height="30" as="geometry" />
        </mxCell>

        <!-- CONNECTORS -->
        <!-- PC to +4 Adder -->
        <mxCell id="e_pc_adder" edge="1" parent="1" source="pc_reg" target="pc_adder" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#16A34A;strokeWidth=2;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <!-- PC to IMEM -->
        <mxCell id="e_pc_imem" edge="1" parent="1" source="pc_reg" target="imem" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#16A34A;strokeWidth=2;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <!-- +4 Loopback to PC -->
        <mxCell id="e_adder_loop" edge="1" parent="1" source="pc_adder" target="pc_reg" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#16A34A;strokeWidth=2;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="380" y="230" />
              <mxPoint x="380" y="105" />
              <mxPoint x="45" y="105" />
              <mxPoint x="45" y="420" />
            </Array>
          </mxGeometry>
        </mxCell>
        <!-- IMEM to RegFile & ImmGen -->
        <mxCell id="e_imem_rf" edge="1" parent="1" source="imem" target="regfile" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0284C7;strokeWidth=2;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e_imem_imm" edge="1" parent="1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0284C7;strokeWidth=2;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="imm_gen">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="390" y="420" as="sourcePoint" />
            <Array as="points">
              <mxPoint x="390" y="720" />
            </Array>
          </mxGeometry>
        </mxCell>
        <!-- RegFile to ALU -->
        <mxCell id="e_rf_alu_rs1" edge="1" parent="1" source="regfile" target="alu" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#EA580C;strokeWidth=2;exitX=1;exitY=0.35;exitDx=0;exitDy=0;entryX=0;entryY=0.3;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e_rf_alu_rs2" edge="1" parent="1" source="regfile" target="alu" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#EA580C;strokeWidth=2;exitX=1;exitY=0.85;exitDx=0;exitDy=0;entryX=0;entryY=0.85;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <!-- ALU to Data RAM & MMIO Bus -->
        <mxCell id="e_alu_dmem" edge="1" parent="1" source="alu" target="dmem" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#9333EA;strokeWidth=2;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e_alu_mmio" edge="1" parent="1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#9333EA;strokeWidth=2;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" target="mmio_bus">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="1030" y="435" as="sourcePoint" />
            <Array as="points">
              <mxPoint x="1030" y="695" />
            </Array>
          </mxGeometry>
        </mxCell>
        <!-- Data RAM to WB MUX -->
        <mxCell id="e_dmem_wb" edge="1" parent="1" source="dmem" target="wb_mux" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#E11D48;strokeWidth=2;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.45;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <!-- MMIO Bus to WB MUX -->
        <mxCell id="e_mmio_wb" edge="1" parent="1" source="mmio_bus" target="wb_mux" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#E11D48;strokeWidth=2;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.8;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1360" y="695" />
              <mxPoint x="1360" y="530" />
            </Array>
          </mxGeometry>
        </mxCell>
        <!-- WriteBack Data Return Loop -->
        <mxCell id="e_wb_loop" edge="1" parent="1" source="wb_mux" target="regfile" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#E11D48;strokeWidth=2.5;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.75;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1650" y="440" />
              <mxPoint x="1650" y="90" />
              <mxPoint x="410" y="90" />
              <mxPoint x="410" y="500" />
            </Array>
          </mxGeometry>
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
    return xml

def generate_fig2_1_xml():
    xml = '''<mxfile host="app.diagrams.net" agent="Antigravity" version="24.0.0">
  <diagram id="fig2_1_diagram" name="Secure_MAC_3Stage">
    <mxGraphModel dx="1600" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="2200" pageHeight="1000" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- Title -->
        <mxCell id="title" parent="1" style="text;html=1;align=center;verticalAlign=middle;resizable=0;points=[];autosize=1;strokeColor=none;fillColor=none;fontSize=22;fontStyle=1;fontColor=#0F172A;" value="VI KIẾN TRÚC BỘ TĂNG TỐC SECURE MAC 3 TẦNG VỚI CƠ CHẾ CED MODULO-3 &amp; SHADOW ROLLBACK" vertex="1">
          <mxGeometry x="300" y="20" width="1600" height="40" as="geometry" />
        </mxCell>

        <!-- STAGE 1 CONTAINER -->
        <mxCell id="st1_box" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F0F9FF;strokeColor=#0284C7;strokeWidth=2;dashed=1;arcSize=4;" vertex="1">
          <mxGeometry x="50" y="80" width="580" height="760" as="geometry" />
        </mxCell>
        <mxCell id="st1_lbl" parent="1" style="text;html=1;align=center;verticalAlign=middle;strokeColor=none;fillColor=none;fontSize=16;fontStyle=1;fontColor=#0369A1;" value="TẦNG 1: TOÁN HẠNG &amp; MÃ HÓA" vertex="1">
          <mxGeometry x="100" y="90" width="480" height="30" as="geometry" />
        </mxCell>

        <!-- Stage 1 Components: Inputs -->
        <mxCell id="in_a" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0284C7;strokeWidth=2;fontSize=14;fontColor=#0F172A;fontStyle=1;" value="A [7:0]&lt;br&gt;&lt;font style=&quot;font-size: 13px; font-weight: normal;&quot;&gt;Signed INT8&lt;/font&gt;" vertex="1">
          <mxGeometry x="80" y="150" width="150" height="80" as="geometry" />
        </mxCell>
        <mxCell id="in_b" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0284C7;strokeWidth=2;fontSize=14;fontColor=#0F172A;fontStyle=1;" value="B [7:0]&lt;br&gt;&lt;font style=&quot;font-size: 13px; font-weight: normal;&quot;&gt;Signed INT8&lt;/font&gt;" vertex="1">
          <mxGeometry x="80" y="300" width="150" height="80" as="geometry" />
        </mxCell>
        <mxCell id="in_c" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0284C7;strokeWidth=2;fontSize=14;fontColor=#0F172A;fontStyle=1;" value="C [31:0]&lt;br&gt;&lt;font style=&quot;font-size: 13px; font-weight: normal;&quot;&gt;Accumulator&lt;/font&gt;" vertex="1">
          <mxGeometry x="80" y="650" width="150" height="80" as="geometry" />
        </mxCell>

        <!-- Stage 1 Processing Units -->
        <mxCell id="mul_8b" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0284C7;strokeWidth=2;fontSize=14;fontColor=#0369A1;" value="&lt;b&gt;&lt;font style=&quot;font-size: 16px;&quot;&gt;Multiplier&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;br&gt;A × B -&gt; 16-bit&lt;br&gt;(Pure LUT logic)" vertex="1">
          <mxGeometry x="290" y="150" width="280" height="150" as="geometry" />
        </mxCell>
        <mxCell id="enc_a" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0284C7;strokeWidth=2;fontSize=14;fontColor=#0369A1;" value="&lt;b&gt;mod3_8b (A)&lt;/b&gt;&lt;br&gt;φ(A) mod 3" vertex="1">
          <mxGeometry x="290" y="360" width="280" height="75" as="geometry" />
        </mxCell>
        <mxCell id="enc_b" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0284C7;strokeWidth=2;fontSize=14;fontColor=#0369A1;" value="&lt;b&gt;mod3_8b (B)&lt;/b&gt;&lt;br&gt;φ(B) mod 3" vertex="1">
          <mxGeometry x="290" y="490" width="280" height="75" as="geometry" />
        </mxCell>
        <mxCell id="enc_c" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0284C7;strokeWidth=2;fontSize=14;fontColor=#0369A1;" value="&lt;b&gt;mod3_32b (C)&lt;/b&gt;&lt;br&gt;φ(C) mod 3" vertex="1">
          <mxGeometry x="290" y="650" width="280" height="80" as="geometry" />
        </mxCell>

        <!-- PIPELINE REGISTER 1 -->
        <mxCell id="reg1" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0284C7;strokeColor=#0369A1;strokeWidth=2;fontSize=16;fontStyle=1;fontColor=#FFFFFF;align=center;" value="R&lt;br&gt;E&lt;br&gt;G&lt;br&gt;&lt;br&gt;1" vertex="1">
          <mxGeometry x="645" y="80" width="45" height="760" as="geometry" />
        </mxCell>

        <!-- STAGE 2 CONTAINER -->
        <mxCell id="st2_box" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFBEB;strokeColor=#D97706;strokeWidth=2;dashed=1;arcSize=4;" vertex="1">
          <mxGeometry x="710" y="80" width="600" height="760" as="geometry" />
        </mxCell>
        <mxCell id="st2_lbl" parent="1" style="text;html=1;align=center;verticalAlign=middle;strokeColor=none;fillColor=none;fontSize=16;fontStyle=1;fontColor=#B45309;" value="TẦNG 2: TÍCH LŨY &amp; DỰ ĐOÁN" vertex="1">
          <mxGeometry x="770" y="90" width="480" height="30" as="geometry" />
        </mxCell>

        <!-- Stage 2 Components -->
        <mxCell id="acc_adder" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#D97706;strokeWidth=2;fontSize=14;fontColor=#0F172A;" value="&lt;b&gt;&lt;font style=&quot;font-size: 16px; color: #B45309;&quot;&gt;32-bit Adder&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;br&gt;mac_result =&lt;br&gt;pipe_product + pipe_c" vertex="1">
          <mxGeometry x="745" y="150" width="300" height="150" as="geometry" />
        </mxCell>
        <mxCell id="homo_pred" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#D97706;strokeWidth=2;fontSize=14;fontColor=#0F172A;" value="&lt;b&gt;&lt;font style=&quot;font-size: 16px; color: #B45309;&quot;&gt;Residue Homomorphism&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;br&gt;φ(A*B) = φ(A)*φ(B) mod 3&lt;br&gt;Expected =&lt;br&gt;[φ(AB) + φ(C)] mod 3" vertex="1">
          <mxGeometry x="745" y="360" width="530" height="370" as="geometry" />
        </mxCell>

        <!-- PIPELINE REGISTER 2 -->
        <mxCell id="reg2" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#D97706;strokeColor=#B45309;strokeWidth=2;fontSize=16;fontStyle=1;fontColor=#FFFFFF;align=center;" value="R&lt;br&gt;E&lt;br&gt;G&lt;br&gt;&lt;br&gt;2" vertex="1">
          <mxGeometry x="1330" y="80" width="45" height="760" as="geometry" />
        </mxCell>

        <!-- STAGE 3 CONTAINER -->
        <mxCell id="st3_box" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F0FDF4;strokeColor=#059669;strokeWidth=2;dashed=1;arcSize=4;" vertex="1">
          <mxGeometry x="1395" y="80" width="720" height="760" as="geometry" />
        </mxCell>
        <mxCell id="st3_lbl" parent="1" style="text;html=1;align=center;verticalAlign=middle;strokeColor=none;fillColor=none;fontSize=16;fontStyle=1;fontColor=#047857;" value="TẦNG 3: CED DOUBLE-CHECK &amp; ROLLBACK" vertex="1">
          <mxGeometry x="1480" y="90" width="550" height="30" as="geometry" />
        </mxCell>

        <!-- Stage 3 Components -->
        <mxCell id="rb_mux" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#059669;strokeWidth=2;fontSize=14;fontColor=#047857;" value="&lt;b&gt;Rollback&lt;br&gt;MUX&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 12px;&quot;&gt;0: mac_res&lt;br&gt;1: Shadow&lt;/font&gt;" vertex="1">
          <mxGeometry x="1510" y="150" width="130" height="120" as="geometry" />
        </mxCell>
        <mxCell id="safe_reg" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#059669;strokeWidth=2;fontSize=14;fontColor=#047857;" value="&lt;b&gt;out [31:0] (Correct MAC)&lt;/b&gt;&lt;br&gt;&lt;br&gt;Stores last valid state&lt;br&gt;(32-bit Safe Reg)" vertex="1">
          <mxGeometry x="1730" y="150" width="230" height="120" as="geometry" />
        </mxCell>
        <mxCell id="mod3_32b_act" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#059669;strokeWidth=2;fontSize=14;fontColor=#047857;" value="&lt;b&gt;mod3_32b&lt;/b&gt;&lt;br&gt;&lt;br&gt;Actual mod3&lt;br&gt;(Cây 4 tầng)" vertex="1">
          <mxGeometry x="1420" y="360" width="170" height="110" as="geometry" />
        </mxCell>
        <mxCell id="double_check_ced" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#059669;strokeWidth=2;fontSize=13;fontColor=#0F172A;align=left;spacingLeft=15;" value="&lt;b&gt;&lt;font style=&quot;font-size: 15px; color: #047857;&quot;&gt;DOUBLE-CHECK CED UNIT&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;br&gt;1. mod3_mismatch = (Exp != Act)&lt;br&gt;2. Bit-Distance Parity Orthogonal&lt;br&gt;3. Sanity Range Anomaly Check&lt;br&gt;    |mac_result| &gt; 3,276,700&lt;br&gt;&lt;b&gt;-&gt; Disagreement = (Mismatch | Anomaly)&lt;/b&gt;" vertex="1">
          <mxGeometry x="1650" y="360" width="430" height="370" as="geometry" />
        </mxCell>

        <!-- SIGNAL BADGES -->
        <mxCell id="badge_prod" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#D97706;strokeWidth=1.5;fontSize=12;fontStyle=1;fontColor=#D97706;" value="16b Prod" vertex="1">
          <mxGeometry x="695" y="210" width="70" height="25" as="geometry" />
        </mxCell>
        <mxCell id="badge_c" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#D97706;strokeWidth=1.5;fontSize=12;fontStyle=1;fontColor=#D97706;" value="pipe_c [31:0]" vertex="1">
          <mxGeometry x="695" y="675" width="85" height="25" as="geometry" />
        </mxCell>
        <mxCell id="badge_mac_res" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#059669;strokeWidth=1.5;fontSize=12;fontStyle=1;fontColor=#059669;" value="mac_result" vertex="1">
          <mxGeometry x="1380" y="200" width="80" height="25" as="geometry" />
        </mxCell>
        <mxCell id="badge_exp" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#059669;strokeWidth=1.5;fontSize=12;fontStyle=1;fontColor=#059669;" value="expected_mod3" vertex="1">
          <mxGeometry x="1385" y="530" width="105" height="25" as="geometry" />
        </mxCell>
        <mxCell id="badge_act" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#059669;strokeWidth=1.5;fontSize=12;fontStyle=1;fontColor=#059669;" value="actual_mod3" vertex="1">
          <mxGeometry x="1595" y="405" width="85" height="25" as="geometry" />
        </mxCell>
        <mxCell id="badge_disagree" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FEF2F2;strokeColor=#DC2626;strokeWidth=1.5;fontSize=12;fontStyle=1;fontColor=#DC2626;" value="disagreement (Rollback=1)" vertex="1">
          <mxGeometry x="1520" y="300" width="165" height="25" as="geometry" />
        </mxCell>
        <mxCell id="badge_restore" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#059669;strokeWidth=1.5;fontSize=12;fontStyle=1;fontColor=#059669;" value="restore" vertex="1">
          <mxGeometry x="1760" y="300" width="60" height="25" as="geometry" />
        </mxCell>

        <!-- STAGE 1 CONNECTORS -->
        <mxCell id="e_a_mul" edge="1" parent="1" source="in_a" target="mul_8b" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0284C7;strokeWidth=2;exitX=1;exitY=0.375;exitDx=0;exitDy=0;entryX=0;entryY=0.2;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e_a_enc" edge="1" parent="1" source="in_a" target="enc_a" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0284C7;strokeWidth=2;exitX=1;exitY=0.75;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e_b_mul" edge="1" parent="1" source="in_b" target="mul_8b" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0284C7;strokeWidth=2;exitX=1;exitY=0.25;exitDx=0;exitDy=0;entryX=0;entryY=0.8;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e_b_enc" edge="1" parent="1" source="in_b" target="enc_b" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0284C7;strokeWidth=2;exitX=1;exitY=0.75;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e_c_enc" edge="1" parent="1" source="in_c" target="enc_c" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0284C7;strokeWidth=2;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- STAGE 1 TO REG 1 -->
        <mxCell id="e_mul_reg" edge="1" parent="1" source="mul_8b" target="reg1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0284C7;strokeWidth=2;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.191;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e_enca_reg" edge="1" parent="1" source="enc_a" target="reg1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0284C7;strokeWidth=2;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.418;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e_encb_reg" edge="1" parent="1" source="enc_b" target="reg1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0284C7;strokeWidth=2;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.589;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e_encc_reg" edge="1" parent="1" source="enc_c" target="reg1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0284C7;strokeWidth=2;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.803;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- STAGE 2 CONNECTORS -->
        <mxCell id="e_reg_acc" edge="1" parent="1" target="acc_adder" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#D97706;strokeWidth=2;entryX=0;entryY=0.5;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="690" y="225" as="sourcePoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="e_reg_homo_a" edge="1" parent="1" target="homo_pred" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#D97706;strokeWidth=2;entryX=0;entryY=0.15;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="690" y="398" as="sourcePoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="e_reg_homo_b" edge="1" parent="1" target="homo_pred" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#D97706;strokeWidth=2;entryX=0;entryY=0.45;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="690" y="528" as="sourcePoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="e_reg_homo_c" edge="1" parent="1" target="homo_pred" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#D97706;strokeWidth=2;entryX=0;entryY=0.85;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="690" y="690" as="sourcePoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="e_reg_c_acc" edge="1" parent="1" target="acc_adder" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#D97706;strokeWidth=2;entryX=0;entryY=0.8;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="715" y="690" as="sourcePoint" />
            <Array as="points">
              <mxPoint x="715" y="270" />
            </Array>
          </mxGeometry>
        </mxCell>

        <!-- STAGE 2 TO REG 2 -->
        <mxCell id="e_acc_reg2" edge="1" parent="1" source="acc_adder" target="reg2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#D97706;strokeWidth=2;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.191;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e_homo_reg2" edge="1" parent="1" source="homo_pred" target="reg2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#D97706;strokeWidth=2;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.612;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- STAGE 3 CONNECTORS -->
        <mxCell id="e_reg2_rb" edge="1" parent="1" target="rb_mux" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=2;entryX=0;entryY=0.5;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="1375" y="210" as="sourcePoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="e_reg2_mod3" edge="1" parent="1" target="mod3_32b_act" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=2;entryX=0;entryY=0.5;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="1400" y="210" as="sourcePoint" />
            <Array as="points">
              <mxPoint x="1400" y="415" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="e_reg2_ced" edge="1" parent="1" target="double_check_ced" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=2;entryX=0;entryY=0.5;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="1375" y="545" as="sourcePoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="e_rb_safe" edge="1" parent="1" source="rb_mux" target="safe_reg" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=2;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e_safe_out" edge="1" parent="1" source="safe_reg" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=3;exitX=1;exitY=0.5;exitDx=0;exitDy=0;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="2080" y="210" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="e_mod3_ced" edge="1" parent="1" source="mod3_32b_act" target="double_check_ced" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=2;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.15;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e_ced_irq" edge="1" parent="1" source="double_check_ced" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#DC2626;strokeWidth=3;exitX=1;exitY=0.5;exitDx=0;exitDy=0;">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="2140" y="545" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="lbl_irq" parent="1" style="text;html=1;align=center;verticalAlign=middle;strokeColor=#DC2626;fillColor=#FEF2F2;fontSize=13;fontStyle=1;fontColor=#DC2626;rounded=1;" value="irq (Fault Detected)" vertex="1">
          <mxGeometry x="2005" y="530" width="140" height="30" as="geometry" />
        </mxCell>
        <mxCell id="e_ced_disagree" edge="1" parent="1" source="double_check_ced" target="rb_mux" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#DC2626;strokeWidth=2;exitX=0.2;exitY=0;exitDx=0;exitDy=0;entryX=0.75;entryY=1;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e_safe_restore" edge="1" parent="1" source="safe_reg" target="rb_mux" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=2;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.25;entryY=1;entryDx=0;entryDy=0;">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1845" y="320" />
              <mxPoint x="1543" y="320" />
            </Array>
          </mxGeometry>
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
    return xml

def main():
    p1 = Path(r'd:\NCKH\reports\figures\fig1_rv32i_5stage_datapath.drawio')
    xml1 = generate_fig1_xml()
    ET.fromstring(xml1)
    p1.write_text(xml1, encoding='utf-8')
    print(f'[SUCCESS] Wrote valid Draw.io XML to {p1}')

    p2 = Path(r'd:\NCKH\reports\figures\fig2_1_secure_mac_3stage.drawio')
    xml2 = generate_fig2_1_xml()
    ET.fromstring(xml2)
    p2.write_text(xml2, encoding='utf-8')
    print(f'[SUCCESS] Wrote valid Draw.io XML to {p2}')

if __name__ == '__main__':
    main()
