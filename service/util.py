from model.entity.Parcel import Deed

import re


def process_label(label):
    cms = None
    section = None
    district = None
    main_plate_number = None
    subsidiary_plate_number = None
    partition = None
    volume_code = None
    volume_number = None
    page_number = None

    f_index = 0
    m_index = 0
    g_index = 0
    aa_index = 0
    m_index = 0
    dd_index = 0
    bb_index = 0
    underline_indexes = [m.start() for m in re.finditer("_", label)]
    underline_index1 = 0
    underline_index2 = 0

    if len(underline_indexes) == 2:
        underline_index1 = underline_indexes[0]
        underline_index2 = underline_indexes[1]

    try:
        try:
            f_index = label.index("F")
            m_index = label.index("M")
            g_index = label.index("G")
            aa_index = label.index("AA")
            m_index = label.index("M")
            bb_index = label.index("BB")
            dd_index = label.index("DD")
        except ValueError as e:
            pass

        cms = label[0:3]
        section = label[3:5]
        district = label[5:7]
        main_plate_number = label[7:f_index]
        subsidiary_plate_number = label[f_index + 1:m_index]
        partition = label[m_index + 1:g_index]
        volume_code = label[dd_index + 2:underline_index1]
        volume_number = label[underline_index1 + 1:underline_index2]
        page_number = label[underline_index2 + 1:bb_index]

    except IndexError as e:
        print("index error: " + str(e))

    print(f"""
            process label:
                cms: {cms}, 
                section: {section}, 
                district: {district}, 
                main_plate_number: {main_plate_number}, 
                subsidiary_plate_number: {subsidiary_plate_number}, 
                partition: {partition}, 
                volume_code: {volume_code}", 
                volume_number: {volume_number}", 
                page_number: {page_number}
          """)

    return Deed(cms=cms,
                section=section,
                district=district,
                main_plate_number=main_plate_number,
                subsidiary_plate_number=subsidiary_plate_number,
                partitioned=partition,
                volume_code=volume_code,
                volume_number=volume_number,
                page_number=page_number)
