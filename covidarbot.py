import os
import re
import time
import logging
import json
import requests
import random

from config import Config
from telegram import telegram

preguntas_frecuentes = {
    "¿Qué es un coronavirus? ¿Qué es el SARS-CoV2? ¿Qué es COVID-19?": [
        "Los coronavirus son una familia de virus que pueden causar enfermedades en animales y en humanos. En los seres humanos pueden causar infecciones respiratorias que van desde un resfrío común hasta enfermedades más graves, como el síndrome respiratorio de Medio Oriente (MERS) y el síndrome respiratorio agudo severo (SRAS-SARS).",
        "Actualmente nos encontramos ante una pandemia (epidemia que se propaga a escala mundial) por un nuevo coronavirus, SARS-CoV-2, que fue descubierto recientemente y causa la enfermedad por coronavirus COVID-19."
    ],
    "¿Cuáles son los síntomas de la COVID-19?": [
        "Las personas con COVID-19 suelen tener síntomas similares a una gripe, como fiebre, cansancio y tos seca.",
        "Algunas personas pueden presentar dolores musculares, congestión nasal, dolor de garganta o diarrea.",
        "La mayoría de las personas (alrededor del 80%) se recupera de la enfermedad en unos 7 días sin necesidad de realizar ningún tratamiento especial.",
        "Alrededor de 1 cada 6 personas que desarrollan COVID-19 puede evolucionar a una enfermedad grave y tener dificultad para respirar, que puede requerir internación.",
        "Las personas mayores y las que padecen afecciones médicas subyacentes, como enfermedad cardiovascular, enfermedad respiratoria o tienen las defensas debilitadas, presentan más riesgo de desarrollar una enfermedad grave.",
        "Las personas que tengan fiebre, tos y dificultad para respirar deben buscar atención médica en forma inmediata."
    ],
    "¿Cuánto dura la infección por COVID-19?": [
        "La duración de la enfermedad varía de persona a persona. Los síntomas leves en un individuo sano pueden desaparecer solos en unos pocos días, generalmente alrededor de una semana. Similar a la gripe, la recuperación de una persona con otros problemas de salud en curso, como una afección respiratoria, puede llevar semanas y, en casos graves, complicarse o ser potencialmente fatal."
    ],
    "¿Cuál es la diferencia entre COVID-19 y la gripe?": [
        "Los síntomas de COVID-19 y la gripe son generalmente muy similares. Ambos causan fiebre y síntomas respiratorios, que pueden variar de leves a graves y a veces ser fatales.",
        "Ambos virus también se transmiten de la misma manera, al toser o estornudar, o por contacto con manos, superficies u objetos contaminados con el virus.",
        "Lavarte las manos, cubrirte con un pañuelo descartable o con el pliegue del codo al toser o estornudar y una buena limpieza del hogar son acciones importantes para prevenir ambas infecciones.",
        "El riesgo de enfermedad grave parece ser mayor para COVID-19 que para gripe. Si bien la mayoría de las personas con COVID-19 tiene síntomas leves, aproximadamente 15% tienen infecciones graves y 5% requieren cuidados intensivos."
    ],
    "La vacuna contra la gripe, ¿es útil contra el coronavirus?": [
        "No, la vacuna antigripal solo previene la influenza. Todavía no existe una vacuna contra el coronavirus COVID-19, por eso es tan importante la prevención.",
        "De todos modos, es importantísimo que los grupos de riesgo ante la gripe (adultos mayores, personas con problemas respiratorios, personal de salud) se apliquen la vacuna contra la influenza como todos los años."
    ],
    "¿Cómo se transmite el virus?": [
        "Se transmite de una persona a otra a través de las gotas procedentes de la nariz o la boca que salen despedidas cuando la persona infectada tose, estornuda o habla, por contacto con manos, superficies u objetos contaminados. Por eso es importante mantener distanciamiento social y tomar precauciones de contacto."
    ],
    "¿Qué puedo hacer para evitar contraer COVID-19?": [
        "Para disminuir el riesgo de contraer COVID-19 sugerimos:",
        " - Distanciamiento social: evitá reuniones, eventos y salir de casa en general, excepto para actividades absolutamente esenciales.",
        " - Mantené la higiene de las manos limpiándolas regularmente con agua y jabón o con alcohol en gel.",
        " - Limpiá tus manos:"
        "  -- antes de entrar y al salir de un área utilizada por otras personas,"
        "  -- después de usar el baño,"
        "  -- después de toser o estornudar,"
        "  -- antes de preparar comida o comer."
        " - Al toser y estornudar, cubrite con pañuelos descartables (desechalos después de usarlos y lavate las manos inmediatamente después) o hacelo en el pliegue del codo si no tenés pañuelos descartables."
        " - Limpiá periódicamente las superficies y los objetos que usás con frecuencia."
        " -  Ventilá los ambientes."
    ],
    "¿Por qué debo lavarme frecuentemente las manos o usar alcohol en gel para evitar la propagación de COVID-19?": [
        "Lavarte las manos con agua y jabón o usar desinfectante a base de alcohol elimina las partículas virales que pueda haber en tus manos."
    ],
    "¿Por qué debo mantener una distancia de 1 metro con otra persona?": [
        "Cuando alguien tose o estornuda, despide por la nariz o por la boca unas gotitas de líquido que pueden contener el virus. Si esa persona tiene la enfermedad y está demasiado cerca de otra, esta puede respirar las gotitas y con ellas el virus de la COVID-19."
    ],
    "¿Por qué debo evitar tocarme los ojos, la nariz y la boca?": [
        "Las manos tocan muchas superficies y pueden contener el virus en su superficie. Una vez contaminadas, pueden transferir el virus a los ojos, la nariz o la boca. Si el virus ingresa puede causar la enfermedad.",
        "Por este motivo es importante lavar las manos frecuentemente o utilizar alcohol en gel."
    ],
    "¿Debo usar barbijo?": [
        "No es necesario que uses barbijo para protegerte, e incluso puede ser contraproducente dado que las manos se contaminan fácilmente al quitarlo. El uso de barbijo es útil únicamente para que las personas con COVID-19 no propaguen la enfermedad.",
        "Solo debes usarlo si se te presentan los síntomas respiratorios característicos de la COVID-19 (fiebre, dolor de garganta, resfrío, tos).",
        "También debe usarlo el personal de salud que asiste a personas con enfermedad respiratoria."
    ],
    "¿Qué significa ser contacto de alguien con COVID-19?": [
        "La siguiente definición es dinámica y puede variar en el transcurso de la pandemia.",
        "",
        "Al día de la fecha se considera “contacto” a toda persona que haya estado cerca (cara a cara durante al menos 15 minutos o en el mismo espacio cerrado durante al menos 2 horas) de una persona que tiene diagnóstico confirmado de COVID-19."
    ],
    "¿Qué debo hacer si entro en contacto con una persona con COVID-19?": [
        "Si sos identificado como contacto de una persona con infección confirmada por COVID-19, debés aislarte durante 14 días contados desde el contacto, controlar tu salud e informar cualquier síntoma."
    ],
    "¿Qué debo hacer si entro en contacto con una persona que fue identificada como contacto de otra persona con infección confirmada?": [
        "Si estuviste en contacto con una persona identificada como contacto cercano de otra persona con infección confirmada por la COVID-19, no necesitás aislarte (aunque el contacto cercano sí tiene que hacerlo) ni tomar ninguna otra precaución especial, más allá de las medidas generales para prevenir o contraer la COVID-19."
    ],
    "¿Puedo adquirir COVID-19 por contacto con una persona asintomática?": [
        "Por el momento, no existe evidencia de trasmisión de la COVID-19 antes de la aparición de síntomas. Según los datos disponibles, las personas con síntomas son la causa más frecuente de propagación del virus."
    ],
    "¿Qué significa distanciamiento social?": [
        "Distanciamiento social significa:",
        " - que dejes una distancia de 1 metro entre vos y otros;",
        " - que evites las multitudes y las reuniones masivas en las que sea difícil mantener la distancia adecuada de los demás;",
        " - que evites pequeñas reuniones en espacios cerrados, como celebraciones familiares;",
        " - que evites dar la mano, abrazar o besar a otras personas;",
        " - que no compartas el mate, vajilla, y utensilios;",
        " - que evites visitar a personas vulnerables, como las que se encuentran en centros de atención para personas mayores u hospitales, bebés o personas con sistemas inmunes comprometidos debido a enfermedades o tratamiento médico.",
        "Podés viajar al trabajo o la escuela en transporte público si no tenés otra forma de viajar. Por favor, <b>tratá de separarte lo más posible de otros pasajeros</b>."
        "El distanciamiento social es una medida efectiva, pero se reconoce que no se puede practicar en todas las situaciones; su objetivo es reducir el potencial de transmisión.",
        "Es importante que todos hagamos nuestra parte para limitar la propagación de la COVID-19; esto ayudará a proteger a las personas vulnerables en nuestra comunidad y reducirá la carga sobre nuestros hospitales."
    ],
    "¿Por qué es importante el distanciamiento social?": [
        "El distanciamiento social es la mejor medida que podemos tomar para disminuir la circulación del SARS-CoV2 causante de la COVID-19.",
        "Debés tener en cuenta que no es siempre posible lograr un distanciamiento social absoluto. De todas formas te recomendamos fuertemente intentar realizarlo con la finalidad de protegerte y proteger a los demás."
    ],
    "¿Existe una cura o vacuna?": [
        "Hasta el momento no hay vacunas que protejan contra COVID-19. Tampoco existe un tratamiento específico.",
        "El diagnóstico temprano y la atención de apoyo general son importantes. La mayoría de las veces, los síntomas se resuelven por sí solos. Las personas que tienen enfermedades graves con complicaciones pueden necesitar ser atendidas en el hospital."
    ],
    "¿Se puede tratar la COVID-19?": [
        "Las infecciones causadas por nuevos coronavirus no tienen tratamiento específico, aunque sí se pueden tratar los síntomas que provoca. El tratamiento de los síntomas va a depender del estado clínico de cada paciente."
    ],
    "¿Puedo contagiarme de COVID-19 por contacto con las heces de una persona que padece la enfermedad?": [
        "El riesgo de contraer la COVID-19 por contacto con las heces de una persona infectada parece ser bajo. Aunque las investigaciones iniciales apuntan a que el virus puede estar presente en las heces en algunos casos, la propagación por esta vía no es uno de los rasgos característicos del brote. No obstante, se trata de un riesgo y, por lo tanto, es una razón más para lavarse las manos con frecuencia, después de ir al baño y antes de comer."
    ],
    "¿Hay personas que presentan más riesgos si se contagian?": [
        "Sí. Las personas mayores de 60, las que tienen enfermedades respiratorias o cardiovasculares y las que tienen afecciones como diabetes presentan mayores riesgos en caso de contagio."
    ],
    "¿Cuándo se considera un caso como sospechoso?": [
        "La definición es dinámica e irá variando con el transcurso del tiempo."
    ],
    "¿Por qué va cambiando la consideración de caso sospechoso?": [
        "<b>La epidemiología de la infección es dinámica, por lo tanto irá variando la sospecha de casos probables.</b> Las personas provenientes de países donde hay circulación activa del virus en la comunidad son consideradas expuestas al virus."
    ],
    "¿Es necesario realizar algún estudio para buscar SARS-CoV-2 en sujetos asintomáticos?": [
        "No. Por el momento, con la evidencia científica disponible, no se recomienda el uso de métodos diagnósticos en casos asintomáticos. De todas formas, las recomendaciones del Ministerio de Salud de la Nación son las que establecen a cuáles personas hay que realizarles los estudios correspondientes."
    ],
    "¿Se realiza algún análisis de sangre u otras muestras biológicas para saber si una persona ha contraído el nuevo coronavirus (SARS-CoV-2)?": [
        "No. El diagnóstico debe realizarse en los laboratorios de referencia, en muestras clínicas respiratorias. Las recomendaciones del Ministerio de Salud de la Nación son las que establecen a cuáles personas hay que realizarles los estudios correspondientes."
    ],
    "¿Quién tiene mayor riesgo de desarrollar una enfermedad grave vinculada a COVID-19?": [
        "Aún falta mucho por aprender sobre esta enfermedad y cómo afecta a los seres humanos, pero, por lo que ha sucedido en otros países que tuvieron la epidemia en estos últimos meses, las personas mayores y las que padecen afecciones médicas preexistentes (como enfermedad cardiovascular, enfermedad respiratoria o defensas debilitadas, diabetes, etc.), desarrollan formas graves de la enfermedad con más frecuencia que otras."
    ],
    "¿Cuánto dura el periodo de incubación de la COVID-19?": [
        "El “período de incubación” es el tiempo que transcurre entre la infección por el virus y la aparición de los síntomas de la enfermedad, que según los datos disponibles oscila entre 1 y 14 días, y en promedio alrededor de 5 días. A modo de comparación, el período de incubación de la gripe es 2 días en promedio y oscila entre 1 y 7. Por esta razón se les pide a las personas que podrían haber estado en contacto con un caso confirmado que se aíslen por 14 días."
    ],
    "Mi animal de compañía, ¿me puede contagiar la COVID-19?": [
        "Aunque hubo un caso de un perro infectado en Hong Kong, hasta la fecha no hay pruebas de que un perro, un gato o cualquier mascota pueda transmitir la COVID-19 ni de que esos animales puedan enfermarse de un ser humano. Igualmente, siguen las investigaciones y el conocimiento sobre esta nueva enfermedad."
    ],
    "¿Cuánto tiempo sobrevive el virus en una superficie?": [
        "Los estudios realizados (incluida la información preliminar disponible sobre el virus de la COVID-19) indican que los coronavirus pueden subsistir en una superficie desde unas pocas horas hasta varios días.",
        "El tiempo puede variar en función de las condiciones (por ejemplo, el tipo de superficie, la temperatura o la humedad del ambiente).",
        "Limpiar con un desinfectante común, lavarte las manos, utilizar alcohol gel y evitar tocarte los ojos, la boca o la nariz disminuye el riesgo de transmisión."
    ],
    "¿Es seguro recibir un paquete de una zona en la que se notificaron casos de COVID-19?": [
        "En general sí es seguro. Si el paquete fue manipulado, transportado y expuesto a diferentes condiciones y temperaturas, tiene muy baja probabilidad que esté contaminado con el virus causante de la COVID-19."
    ],
    "Viajé a un país considerado de alto riesgo para COVID-19, ¿qué tengo que hacer?": [
        "Dado que la epidemiología de la infección por la COVID-19 es dinámica, te sugerimos que consultes cuáles son los países considerados de riesgo ( /Zonas ).",
        "Si estuviste, saliste de, o transitaste por un país de mayor riesgo en los últimos 14 días, debés autoaislarte de los demás durante 14 días contados a partir del día en que saliste del país afectado,",
        "y controlarte para detectar síntomas.",
        "Si desarrollás fiebre o síntomas respiratorios, contactate con el sistema de salud",
        "En caso de dificultad respiratoria, o si tus síntomas son graves, llamá a emergencias identificándote inmediatamente, informá al personal a dónde viajaste o si estuviste en contacto con un caso confirmado.",
        "Si tenés síntomas, es importante que no vayas al trabajo, la escuela, la universidad, la guardería, el gimnasio o las áreas públicas, y no debés usar el transporte público, los taxis o los servicios de transporte compartido."
    ],
    "Viajé a un país que no se considera de riesgo para la COVID-19, ¿qué tengo que hacer?": [
        "Se cree que el riesgo de exposición a la enfermedad COVID-19 es más alto para las personas que viajaron a través de un país con circulación local del virus. Sin embargo, hay un número cada vez mayor de otros países en riesgo de COVID-19.",
        "Si desarrollás fiebre o síntomas respiratorios, por favor contactate con el sistema de salud.",
        "En caso de dificultad respiratoria, o si sus síntomas son graves, llamá a emergencias, informá al personal a dónde viajaste o si estuviste en contacto con un caso confirmado.",
        "Si viajaste a otro país en los últimos 14 días, debés autocontrolarte para detectar síntomas, practicar el distanciamiento social e inmediatamente aislarte si no te encontrás bien.",
        "Si tenés síntomas, es importante que no vayas al trabajo, la escuela, la universidad, la guardería, el gimnasio o las áreas públicas, y no debés usar el transporte público, los taxis o los servicios de transporte compartido."
    ],
    "¿Puedo hacer un viaje?": [
        "Actualmente se recomienda no viajar, excepto que sea estrictamente necesario. Si debés hacerlo, tomá todas las medidas de prevención."
    ],
    "¿Cómo realizo el aislamiento domiciliario de una persona con COVID-19?": [
        "Consultá la información que te presentamos en la sección “Recomendaciones para la población”. /Aislamiento "
    ],
    "¿Dónde puedo consultar información actualizada y veraz sobre la COVID-19?": [
        "En la era de las comunicaciones, la desinformación es moneda corriente y peligrosa. Eventos como la pandemia por la COVID-19 nos pone en la necesidad de obtener información al instante, por tal motivo es frecuente la difusión de contenidos falsos o erróneos.",
        "Es nuestra responsabilidad evitar la difusión de información falsa o maliciosa. Es clave que no actuemos como amplificadores de noticias falsas, que en general buscan un impacto emocional rápido para su viralización.",
        "Para evitar confusiones, debés buscar información en sitios cuentas de redes sociales que permitan comprobar su veracidad, como los del Ministerio de Salud de la República Argentina, de la Organización Mundial de la Salud o de la Organización Panamericana de la Salud.",
        "Desconfiá de —y no difundas— rumores, mensajes y audios de Whatsapp provenientes de supuestas autoridades en la materia que difundan información que no pueda ser verificada."
    ],
    "Soy argentino y estoy de viaje en un país afectado por el coronavirus. ¿Voy a poder regresar?": [
        "Si.",
        "Consultá los vuelos autorizados: https://www.argentina.gob.ar/coronavirus/vuelos-autorizados",
        "Podés escribirnos por cualquier consulta, dependiendo de dónde te encuentres a estos correos electrónicos:",
        "- Europa: covideuropa@cancilleria.gob.ar",
        "- Estados Unidos y Canadá: covidnorte@cancilleria.gob.ar",
        "- América Central, Caribe y México: covidcentral@cancilleria.gob.ar",
        "- América del Sur: covidsur@cancilleria.gob.ar",
        "- Asia, Oceanía, Africa y Medio Oriente: covidrestmun@cancilleria.gob.ar"
        "Conocé más en el sitio de ANAC: https://www.anac.gov.ar/anac/web/#&panel1-3"
    ],
    "¿Qué hago si alguien no cumple la cuarentena?": [
        "El artículo 7 del Decreto 260/2020 determina que, en caso de verificarse el incumplimiento del aislamiento indicado y demás obligaciones establecidas, los funcionarios o funcionarias, personal de salud, personal a cargo de establecimientos educativos y autoridades en general que tomen conocimiento de tal circunstancia deberán radicar denuncia penal para investigar la posible comisión de los delitos previstos en los artículos 205, 239 y concordantes del Código Penal.",
        "Con el fin de controlar la trasmisión del COVID- 19, la autoridad sanitaria competente, además de realizar las acciones preventivas generales, realizará el seguimiento de la evolución de las personas enfermas y el de las personas que estén o hayan estado en contacto con las mismas",
        "Para denunciar a quienes violen la cuarentena, comunicate con el Ministerio de Seguridad al número gratuito 134 desde cualquier lugar del país."
    ]

}


mitos_oms = {
    "El virus COVID-19 puede transmitirse en zonas con climas cálidos y húmedos": [
        "Las pruebas científicas obtenidas hasta ahora indican que el virus de la COVID-19 puede transmitirse en CUALQUIER ZONA, incluidas las de clima cálido y húmedo. Con independencia de las condiciones climáticas, hay que adoptar medidas de protección si se vive en una zona donde se hayan notificado casos de COVID-19 o si se viaja a ella. La mejor manera de protegerse contra la COVID-19 es lavarse las manos con frecuencia. De esta manera se eliminan los virus que puedan estar en las manos y se evita la infección que podría producirse al tocarse los ojos, la boca y la nariz. "
    ],
    "El frío y la nieve NO PUEDEN matar el nuevo coronavirus (2019-nCoV)": [
        "La temperatura normal del cuerpo humano se mantiene en torno a 36,5° y 37°, con independencia de la temperatura exterior o de las condiciones meteorológicas. Por lo tanto, no hay razón para creer que el frío pueda matar el nuevo coronavirus o acabar con otras enfermedades. La forma más eficaz de protegerse contra el 2019-nCoV es limpiarse las manos frecuentemente con un desinfectante a base de alcohol o con agua y jabón."
    ],
    "Bañarse en agua caliente no previene la infección por el nuevo coronavirus": [
        "Bañarse en agua caliente no proporciona ninguna protección contra la COVID-19. Con independencia de la temperatura del agua de la bañera o la ducha, la temperatura corporal continuará siendo de 36,5 °C a 37 °C. De hecho, si el agua está muy caliente puede uno quemarse. Lo mejor que se puede hacer para protegerse de la COVID-19 es lavarse las manos con frecuencia para eliminar los virus que pueda haber en su superficie y no contagiarnos al tocarnos los ojos, la boca y la nariz."
    ],
    "El nuevo coronavirus NO PUEDE transmitirse a través de picaduras de mosquitos": [
        "El nuevo coronavirus es un virus respiratorio que se propaga principalmente por contacto con una persona infectada a través de las gotículas respiratorias que se generan cuando esta persona tose o estornuda, por ejemplo, o a través de gotículas de saliva o secreciones de la nariz. Hasta la fecha no hay información ni pruebas que indiquen que el 2019-nCoV pueda transmitirse por medio de mosquitos. Para protegerse, evite el contacto cercano con cualquier persona que tenga fiebre y tos, y practique una buena higiene de las manos y de las vías respiratorias."
    ],
    "¿Se puede matar el nuevo coronavirus con un secador de manos?": [
        "No. Los secadores de manos no matan el 2019-nCoV. Para protegerse contra el nuevo coronavirus (2019-nCoV), lávese las manos frecuentemente con un gel hidroalcohólico o con agua y jabón. Una vez limpias, séqueselas bien con toallitas de papel o con un secador de aire caliente."
    ],
    "¿Se puede matar el 2019-nCoV con una lámpara ultravioleta para desinfección?": [
        "No se deben utilizar lámparas ultravioletas para esterilizar las manos u otras partes del cuerpo, ya que la radiación ultravioleta puede causar eritemas (irritación de la piel)."
    ],
    "¿Se puede matar el nuevo coronavirus rociando el cuerpo con alcohol o con cloro?": [
        "No. Rociar todo el cuerpo con alcohol o cloro no sirve para matar los virus que ya han entrado en el organismo. Pulverizar estas sustancias puede dañar la ropa y las mucosas (es decir, los ojos, la boca, etc.). Tanto el alcohol como el cloro pueden servir para desinfectar las superficies, siempre que se sigan las recomendaciones pertinentes. ",
        "",
        "Hay varias medidas que se pueden aplicar para protegerse del nuevo coronavirus. Empiece por limpiarse las manos con frecuencia con un gel hidroalcohólico o con agua y jabón."
    ],
    "Las vacunas contra la neumonía, ¿protegen contra el nuevo coronavirus?": [
        "No. Las vacunas contra la neumonía, como la neumocócica y la vacuna contra Haemophilus influenzae de tipo B (Hib), no protegen contra el nuevo coronavirus.",
        "",
        "El 2019-nCoV es tan nuevo y diferente que es necesario desarrollar una vacuna específica, en la que ya se está trabajando con el apoyo de la OMS.",
        "",
        "Aunque las vacunas contra la neumonía no son eficaces contra el 2019‑nCoV, es muy conveniente vacunarse contra las enfermedades respiratorias para mantener una buena salud."
    ],
    "¿Conviene enjuagarse regularmente la nariz con una solución salina para prevenir la infección por el nuevo coronavirus?": [
        "No. No hay pruebas que indiquen que esta práctica proteja de la infección por el nuevo coronavirus.",
        "",
        "Aunque algunas pruebas indican que enjuagarse la nariz regularmente con solución salina puede acelerar la recuperación tras un resfriado común, no se ha demostrado que prevenga las infecciones respiratorias."
    ],
    "¿Comer ajo puede ayudar a prevenir la infección por el nuevo coronavirus?": [
        "El ajo es un alimento saludable que puede tener algunas propiedades antimicrobianas. Sin embargo, no se han obtenido pruebas de que comerlo proteja contra el virus que causa el brote actual."
    ],
    "El nuevo coronavirus, ¿afecta solo a las personas de edad o también puede afectar a las más jóvenes?": [
        "El nuevo coronavirus (2019-nCoV) puede infectar a personas de todas las edades, si bien se ha observado que las personas mayores y las que padecen algunas enfermedades (como el asma, la diabetes o las cardiopatías) tienen más probabilidades de enfermarse gravemente cuando adquieren la infección.",
        "",
        "La OMS aconseja a las personas de todas las edades que tomen medidas para protegerse del virus, por ejemplo, mediante una buena higiene de manos y respiratoria."
    ],
    "¿Son eficaces los antibióticos para prevenir y tratar la infección por el nuevo coronavirus?": [
        "No. Los antibióticos son eficaces contra las bacterias, pero no contra los virus.",
        "",
        "Puesto que el nuevo coronavirus (2019-nCoV) es un virus, no deben utilizarse antibióticos ni para prevenir ni para tratar la infección.",
        "",
        "Sin embargo, si resulta usted infectado por este virus y le hospitalizan, es posible que le administren antibióticos para que no contraiga infecciones bacterianas."
    ],
    "¿Hay algún medicamento para prevenir o tratar la infección por el nuevo coronavirus?": [
        "Por el momento, no se recomienda ningún medicamento específico para prevenir o tratar la infección por el nuevo coronavirus (2019-nCoV).",
        "",
        "Sin embargo, es necesario atender adecuadamente a las personas infectadas por este virus para aliviar y tratar los síntomas y procurar medidas de apoyo optimizadas a los que presenten síntomas graves. Se están estudiando algunos tratamientos específicos que se probarán en ensayos clínicos. La OMS está ayudando a agilizar las labores de investigación y desarrollo con una serie de asociados."
    ]
}


def faq2menu(preguntas_frecuentes, prefix, menu):
    faqs = []
    faq_answers = {}
    i = 0
    for pfi in preguntas_frecuentes:
        command = "/{}{}".format(prefix, i)
        faqs.append(" ❓ {} {}".format(pfi, command))
        faq_answers[command] = ["<b>{}</b>".format(pfi), "-"] + preguntas_frecuentes[pfi] + menu
        i += 1
    return faqs, faq_answers


menu_principal = "\n🔸 Menú principal /start"
cuidados = " - Cuidados /Cuidados"
aislamiento = " - Aislamiento /Aislamiento"
medidas = " - Medidas /Medidas"
preguntas = " - Preguntas /Preguntas"
preguntas = " - Rumores /Rumores"


faqs, faq_answers = faq2menu(preguntas_frecuentes, "faq", [menu_principal + preguntas])

oms_faqs, oms_faq_answers = faq2menu(mitos_oms, "rumor", [menu_principal + preguntas])

answers = {
    "/help": [
        "Bot informativo creado por @Eibriel",
        "Fuentes:",
        "- Ministerio de Salud de Argentina",
        "Código fuente:",
        "- https://github.com/Eibriel/CovidArBot",
        menu_principal
    ],
    "/start": [
        "Información del <b>Ministerio de Salud</b> y la <b>Organización Mundial de la Salud</b>",
        "",
        "🔹 ¿Qué podemos hacer para cuidarnos? /Cuidados",
        "🔹 ¿Qué medidas está tomando el gobierno? /Medidas",
        "🔹 Informe diario /Informe",
        "🔹 Preguntas frecuentes /Preguntas",
        "🔹 Teléfonos y contactos útiles /Telefonos",
        # Eliminado el 2020-03-24
        # "🔹 Plan Operativo de preparación y respuesta al COVID-19 /Plan",
        # El plan operativo se reemplaza por Recomendaciones para equipos de salud
        "🔹 Recomendaciones para equipos de salud /Salud",
        "🔹 [Nuevo] Descargá la app de autoevaluación de síntomas de COVID-19 /Autotest",
        "",
        "🔹 [Nuevo] Pautas a seguir durante el aislamiento /AislamientoSocialPautas",
        "🔹 [Nuevo] Recomendaciones para salir de casa /AislamientoSocialSalidas",
        "🔹 [Nuevo] Para sacar al perro /AislamientoSocialPerros",
        "",
        "🔹 [Nuevo] Servicios y enlaces útiles mientras estés en casa /AislamientoSocialServicios",
        "",
        "🔹 [Nuevo] Acerca de los rumores sobre el nuevo coronavirus /Rumores",
        "",
        "Última actualización: <b>2020-03-24</b>",
        menu_principal
    ],
    # Cuidados
    "/Cuidados": [
        "<b>¿Qué podemos hacer para cuidarnos?</b>",
        "",
        "🔹 Población general /General",
        "🔹 Mayores de 60 años, embarazadas y personas con patologías crónicas /Mayores",
        "🔹 Aislamiento para casos confirmados y casos sospechosos /Aislamiento",
        "🔹 Indicaciones para viajeros (en el país). Aislamiento preventivo /Viajeros",
        "",
        "https://www.youtube.com/watch?v=uyv9lprlx3k",
        menu_principal
    ],
    # Cuidados -> General
    "/General": [
        "Los síntomas más comunes son fiebre, tos, dolor de garganta y cansancio.",
        "Algunos casos pueden presentar complicaciones y requerir hospitalización.",
        "Puede afectar a cualquier persona, el riesgo de complicaciones aumenta en mayores de 60 años y personas con afecciones preexistentes (enfermedad cardiovascular, diabetes y enfermedad respiratoria crónica entre otras).",
        "En caso de presentar síntomas, aunque sean leves, consultar telefónicamente al sistema de salud. Ejemplo: 107 en CABA, 148 en Provincia de Buenos Aires, 0800-222-1002 a nivel nacional.",
        "PHOTO|https://ibin.co/5GcehnJxTU2B.jpg|Cuidados generales",
        menu_principal + cuidados
    ],
    # Cuidados -> Mayores
    "/Mayores": [
        "<b>Reforzar las recomendaciones de prevención de infecciones respiratorias:</b>",
        "- Distanciamiento social (mantener un metro de distancia entre personas)",
        "- Lavarse las manos frecuentemente con agua y jabón o alcohol en gel.",
        "- Toser o estornudar sobre el pliegue del codo o utilizar pañuelos descartables.",
        "- No llevarse las manos a la cara.",
        "- Ventilar bien los ambientes de la casa y del lugar de trabajo.",
        "- Desinfectar bien los objetos que se usan con frecuencia.",
        "- No automedicarse.",
        "- En caso de presentar síntomas, aunque sean leves, consultar inmediatamente al sistema de salud, siguiendo las recomendacionesl ocales , para saber cómo hacer correctamente la consulta. Ejemplo: 107 en CABA, 148 en Provincia de Buenos Aires, 0800-222-1002 a nivel nacional.",
        "",
        "<b>En la medida de lo posible, delegar la realización de mandados o compra de medicamentos a personas de confianza o del entorno familiar que no pertenezcan a los grupos de riesgo.</b>",
        "",
        "Las personas mayores de 60 años, embarazadas o quienes están dentro de los grupos de riesgo <b>no deben convivir con personas que vengan desde el exterior.</b>",
        "",
        "Vacunarse contra la gripe y el neumococo, de acuerdo al calendario de vacunación nacional.",
        "",
        "Información sobre licencia laboral para mayores de 60 años, embarazadas y menores de 60 años con factores de riesgo /LicenciaMayores60",
        "PHOTO|https://ibin.co/5GkUzRTrggz1.jpg|Cuidados para mayores de 65 años",
        menu_principal + cuidados
    ],
    "/LicenciaMayores60": ["https://www.argentina.gob.ar/sites/default/files/207.pdf"],
    # Cuidados -> Aislamiento
    "/Aislamiento": [
        "🔹 Casos confirmados /Confirmados",
        "🔹 Casos sospechosos /Sospechosos",
        menu_principal + cuidados
    ],
    # Cuidados -> Aislamiento -> Confirmados
    "/Confirmados": [
        "Las personas que están en su domicilio porque poseen confirmación médica de haber contraído COVID-19 o porque están esperando diagnóstico definitivo, es decir que entran en la definición de caso sospechoso, deben MANTENER AISLAMIENTO ESTRICTO HASTA EL ALTA MÉDICA.",
        "Esto implica que:",
        "- No deben salir del domicilio.",
        "- No deben recibir visitas.",
        "- No deben haber presencia de personas mayores de 60 años en la misma vivienda.",
        "- Siempre que sea posible, deben permanecer en una misma habitación individual, evitando transitar por zonas comunes de la casa.",
        "- No deben tener contacto estrecho con otras personas (distancia mínima de 1 metro)",
        "- Deben lavarse las manos con agua y jabón o alcohol en gel periódicamente.",
        "- Al toser o estornudar, deben cubrirse la nariz y la boca con el pliegue interno del codo, o usar pañuelo descartable (y desecharlo inmediatamente).",
        "- No debe compartir utensilios de cocina (plato, vaso, cubiertos, mate, etc.). Todo esto deberá limpiarse con agua y detergente luego del uso.",
        "- Los elementos de aseo deben ser de uso exclusivo (jabón, toalla). Se deberán lavar luego de su uso.",
        "- Deben ventilar adecuadamente los ambientes.",
        "- Debe limpiar y desinfectar las superficies y objetos de uso frecuente (especialmente mesas, mesadas, sillas, escritorios y otros utilizados diariamente). Esto se hará de la siguiente manera:",
        " 1 Lavar con una solución de agua y detergente.",
        " 2 Enjuagar con agua limpia.",
        " 3 Desinfectar con una solución de 10 ml (2 cucharadas soperas) de lavandina de uso comercial en 1 litro de agua.",
        "- No debe viajar.",
        "",
        "<b>Contactos estrechos de casos confirmados:</b>",
        "Un contacto estrecho es cualquier persona que haya permanecido a una distancia menor a 1 metro, (ej. convivientes, visitas) con una persona que presentaba síntomas y luego fue confirmada por coronavirus.",
        "Estas personas deben mantener aislamiento domiciliario durante 14 días desde el último contacto con el caso confirmado o bien, en caso de ser convivientes, 14 días desde el último día en que el caso confirmado presentó síntomas. En todas estas situaciones cada persona deberá cumplir con las siguientes medidas:",
        "- No deben tener contacto estrecho con otras personas (distancia mínima de 1 metro).",
        "- No deben salir del domicilio.",
        "- No deben recibir visitas.",
        "- No deben haber presencia de personas mayores de 60 años en la misma vivienda.",
        "- Deben lavarse las manos con agua y jabón o alcohol en gel periódicamente.",
        "- Al toser o estornudar, deben cubrirse la nariz y la boca con el pliegue interno del codo, o usar pañuelo descartable (y desecharlo inmediatamente).",
        "- No deben compartir utensilios de cocina (plato, vaso, cubiertos, mate, etc.). Todo esto deberá limpiarse con agua y detergente luego del uso.",
        "- Los elementos de aseo deben ser de uso exclusivo (jabón, toalla). Se deberán lavar luego de su uso.",
        "- Deben ventilar adecuadamente los ambientes.",
        "- Deben limpiar y desinfectar las superficies y objetos de uso frecuente (especialmente mesas, mesadas, sillas, escritorios y otros utilizados diariamente). Esto se hará de la siguiente manera:",
        " -- Lavar con una solución de agua y detergente.",
        " -- Enjuagar con agua limpia.",
        " -- Desinfectar con una solución de 10 ml (2 cucharadas soperas) de lavandina de uso comercial en 1 litros de agua.",
        "- Ante la presencia de síntomas (tos o fiebre o dolor de garganta o falta de aire), comunicarse (idealmente de manera telefónica) inmediatamente con el servicio de salud.",
        menu_principal + cuidados + aislamiento
    ],
    # Cuidados -> Aislamiento -> Sospechosos
    "/Sospechosos": [
        "Las personas que están en su domicilio porque poseen confirmación médica de haber contraído COVID-19 o porque están esperando diagnóstico definitivo, es decir que entran en la definición de caso sospechoso, deben MANTENER AISLAMIENTO ESTRICTO HASTA EL ALTA MÉDICA.",
        "Esto implica que:",
        "- No deben salir del domicilio.",
        "- No deben recibir visitas.",
        "- No deben haber presencia de personas mayores de 60 años en la misma vivienda.",
        "- Siempre que sea posible, deben permanecer en una misma habitación individual, evitando transitar por zonas comunes de la casa.",
        "- No deben tener contacto estrecho con otras personas (distancia mínima de 1 metro)",
        "- Deben lavarse las manos con agua y jabón o alcohol en gel periódicamente.",
        "- Al toser o estornudar, deben cubrirse la nariz y la boca con el pliegue interno del codo, o usar pañuelo descartable (y desecharlo inmediatamente).",
        "- No debe compartir utensilios de cocina (plato, vaso, cubiertos, mate, etc.). Todo esto deberá limpiarse con agua y detergente luego del uso.",
        "- Los elementos de aseo deben ser de uso exclusivo (jabón, toalla). Se deberán lavar luego de su uso.",
        "- Deben ventilar adecuadamente los ambientes.",
        "- Debe limpiar y desinfectar las superficies y objetos de uso frecuente (especialmente mesas, mesadas, sillas, escritorios y otros utilizados diariamente). Esto se hará de la siguiente manera:",
        " 1 Lavar con una solución de agua y detergente.",
        " 2 Enjuagar con agua limpia.",
        " 3 Desinfectar con una solución de 10 ml (2 cucharadas soperas) de lavandina de uso comercial en 1 litro de agua.",
        "- No debe viajar.",
        "",
        "Para las personas que entran en la definición de caso sospechoso, es decir, que están esperando diagnóstico definitivo por COVID-19:",
        "Deben seguir todo lo explicitado en el punto anterior: mantener aislamiento estricto hasta diagnóstico definitivo. Y:",
        "- Si es descartado, no requiere continuar con el aislamiento estricto.",
        "- Si se confirma el diagnóstico, deben mantener aislamiento estricto hasta el alta médica tal como está indicado en el punto anterior.",
        menu_principal + cuidados + aislamiento
    ],
    # Cuidados -> Aislamiento -> Viajeros
    "/Viajeros": [
        "<b>Prohibición del ingreso al territorio nacional de personas extranjeras no residentes por el plazo de 15 días</b>",
        "Esta decisión minimizará la posibilidad de ingreso y la propagación del virus al interior de nuestra región. Estaremos colaborando con las autoridades de los países vecinos en intercambio de información clave para lograr el objetivo en común. Además, hemos detectado personas que descienden de un avión de zonas de riesgo en un país vecino e intentan ingresar al nuestro por la frontera.",
        "⚠️",
        "<b>No podrán ingresar ni permanecer en el territorio nacional</b> los extranjeros no residentes en el país que no den cumplimiento a la normativa sobre aislamiento obligatorio y a las medidas sanitarias vigentes, salvo excepciones dispuestas por la autoridad sanitaria o migratoria.",
        "",
        "<b>Quienes no cumplan con el aislamiento</b> serán denunciados penalmente para investigar la posible comisión de los delitos previstos en los artículos 205, 239 y concordantes del Código Penal.",
        "⚠️",
        "<b>Las personas que presenten síntomas compatibles con COVID-19 deberán reportarlo telefónicamente de inmediato al sistema de salud. Ejemplo: 107 en CABA, 148 en Provincia de Buenos Aires, 0800-222-1002 a nivel nacional.</b>",
        "",
        "<b>Aislamiento preventivo obligatorio</b>",
        "Personas que vengan desde el exterior deben mantener aislamiento domiciliario durante 14 días desde el ingreso al país.",
        "- Deben permanecer en forma estricta en su domicilio.",
        "- No deben recibir visitas en el hogar.",
        "- No deben tener contacto estrecho con otras personas (distancia mínima de 1 metro).",
        "- Las personas mayores de 60 años, embarazadas o quienes están dentro de los grupos de riesgo (enfermedad cardiovascular, diabetes y enfermedad respiratoria crónica, entre otras) no deben convivir con personas que vengan desde el exterior.",
        "- En la medida de lo posible, delegar la realización de mandados o compra de medicamentos a personas de confianza o del entorno familiar que no pertenezcan a grupos de riesgo.",
        "- Deben lavarse las manos con agua y jabón o alcohol en gel periódicamente.",
        "- Al toser o estornudar, deben cubrirse la nariz y la boca con el pliegue interno del codo, o usar pañuelo descartable (y desecharlo inmediatamente).",
        "- Deben ventilar adecuadamente los ambientes.",
        "- No deben compartir utensilios de cocina (plato, vaso, cubiertos, mate, etc.). Todo esto deberá limpiarse con agua y detergente luego del uso.",
        "- Los elementos de aseo deben ser de uso exclusivo (jabón, toalla). Se deberán lavar luego de su uso.",
        menu_principal + cuidados + aislamiento
    ],
    "/Zonas": ["https://www.argentina.gob.ar/coronavirus/zonas-transmision-local"],
    # Medidas
    "/Medidas": [
        "<b>Aislamiento social, preventivo y obligatorio</b> /AislamientoSocial",
        "El DNU 297/2020 establece el aislamiento social, preventivo y obligatorio hasta el 31 de marzo de 2020 para todas las personas que se encuentren en el país.",
        "",
        "<b>Decreto de Necesidad y Urgencia 260/2020</b> /DNU2602020",
        "El DNU amplía la Emergencia Sanitaria y dispone la adopción de medidas para contener la propagación del nuevo coronavirus.",
        menu_principal
    ],
    # Medias -> AislamientoSocial
    "/AislamientoSocial": [
        "El aislamiento social, preventivo y obligatorio es una medida excepcional que el Gobierno nacional adopta en un contexto crítico.",
        "<b>Con el fin de proteger la salud pública, todas las personas</b> que habitan en el país o se encuentren en él en forma temporaria deberán permanecer en sus domicilios habituales o en donde se encontraban a las 00:00 horas del día 20 de marzo de 2020.",
        "<b>Hasta el 31 de marzo inclusive, deberán abstenerse de concurrir a sus lugares de trabajo y no podrán circular por rutas, vías y espacios públicos</b>.",
        "Solo podrán realizar <b>desplazamientos mínimos e indispensables</b> para <b>aprovisionarse de artículos de limpieza, medicamentos y alimentos</b>.",
        "Durante la vigencia del aislamiento no podrán realizarse eventos culturales, recreativos, deportivos, religiosos ni de ninguna otra índole que impliquen la concurrencia de personas.",
        "También se suspende la apertura de locales, centros comerciales, establecimientos mayoristas y minoristas, y cualquier otro lugar que requiera la presencia de personas.",
        "",
        "✅ Reduciendo el contacto, se reducirán las posibilidades de contagio.",
        "",
        "¿Por qué debemos cumplir con el aislamiento? /AislamientoSocialRazones",
        menu_principal + medidas
    ],
    # Medidas -> AislamientoSocial -> Razones
    "/AislamientoSocialRazones": [
        "<b>¿Por qué debemos cumplir con el aislamiento?</b>",
        "El 11 de marzo de 2020, la Organización Mundial de la Salud declaró al brote del nuevo coronavirus (COVID-19) como una pandemia y, a raíz de ello, nuestro país amplió la Emergencia Sanitaria y le brindó al Ministerio de Salud la facultad para tomar todas las medidas necesarias a fin de minimizar el contagio y fortalecer la capacidad de respuesta del sistema sanitario.",
        "En este marco, atendiendo a las recomendaciones de los organismos internacionales especializados y de los expertos locales, y a la luz de la experiencia de otros países, se determinó que la mejor forma que tenemos para enfrentar la propagación del virus y así cuidar de la salud de todos y todas es el aislamiento.",
        "",
        "✅ Reduciendo el contacto, se reducirán las posibilidades de contagio.",
        menu_principal + medidas
    ],
    # Medidas -> AislamientoSocial -> Pautas
    "/AislamientoSocialPautas": [
        "Para cuidarnos entre todos, es importante que respetemos las siguientes indicaciones:",
        " - Que todo el grupo familiar o conviviente permanezca en el domicilio todos los días.",
        " - Mantené 1 metro de distancia con otras personas.",
        " - No recibas ni hagas visitas.",
        " - Evitá transitar en la vía pública, salvo para hacer compras imprescindibles (alimentos, medicación y artículos de limpieza) o por cuestiones de salud.",
        " - Lavate frecuentemente las manos con agua y jabón o con alcohol en gel .",
        " - Si vas a toser o estornudar, cubrite nariz y boca con el pliegue interno del codo, o usá pañuelo descartable y tiralo inmediatamente en un cesto de residuos.",
        " - Ventilá adecuadamente los ambientes.",
        " - No compartas mate, vajilla ni demás objetos de uso personal.",
        " - Limpialos con agua y detergente después de cada uso.",
        " - Limpiá y desinfectá superficies y objetos de uso frecuente (mesas, mesadas, sillas y otros utilizados diariamente) de la siguiente manera:",
        " -- Lavá con una solución de agua y detergente.",
        " -- Enjuagá con agua limpia.",
        " -- Desinfectá con una solución de 10 ml (2 cucharadas soperas) de lavandina de uso comercial en 1 litros de agua",
        " - Las personas mayores de 60 años, embarazadas o quienes están dentro de los grupos de riesgo no deben convivir con quienes volvieron de zonas afectadas.",
        " - Ante la presencia de síntomas (fiebre de 38° acompañada de tos, dolor de garganta, cansancio o falta de aire), comunicate telefónicamente y de inmediato con el servicio de salud de tu jurisdicción /Telefonos .",
        " - Es importante cuidar especialmente a las personas mayores de 60, mujeres embarazadas y quienes tengan afecciones crónicas (enfermedad cardiovascular, diabetes y enfermedad respiratoria crónica, entre otras).",
        " - En la medida de lo posible, delegá la realización de mandados o compra de medicamentos a personas de confianza o del entorno familiar que no pertenezcan a los grupos de riesgo.",
        "",
        "▶️ Cuidarte es cuidarnos.",
        menu_principal + medidas
    ],
    # Medidas -> AislamientoSocial -> Salida
    "/AislamientoSocialSalidas": [
        "<b>Al momento de ir a la farmacia o hacer compras de primera necesidad</b>",
        " - Pueden ir <b>quienes no presenten síntomas</b> (fiebre de 38° acompañada de tos, dolor de garganta, cansancio o falta de aire).",
        " - Siempre que se pueda, <b>deben quedarse en casa</b> las personas mayores de 60 años, mujeres embarazadas y quienes tienen afecciones crónicas.",
        " - Solo debe salir <b>una persona</b>.",
        " - <b>Preguntá a tus vecinos si necesitan algún producto</b>. Podés dejarlos en la puerta de su casa.",
        "",
        "<b>En el comercio</b>",
        " - <b>Mantené una distancia de 1 metro</b> de los demás y evitá los lugares con muchas personas.",
        " - <b>Evitá tocarte la cara</b>.",
        " - <b>Si vas a toser o estornudar</b>, hacelo en el pliegue del codo.",
        " - <b>No toques los productos</b> si no es necesario. Pensar de antemano qué se necesita comprar.",
        " - <b>Comprá cantidades razonables</b>, sin exagerar: <b>seamos considerados con los demás</b>.",
        " - De ser posible, <b>pagá con tarjeta</b>.",
        "",
        "<b>¿Cómo cuidarnos al regresar a casa?</b>",
        " - Al volver a casa, <b>tratá no tocar nada antes de lavarte bien las manos</b>.",
        " - Dejá en la entrada bolsos, cartera, llaves, abrigo, etc.",
        " - <b>Desinfectá el celular, anteojos, abrigos</b> u otros con alcohol al 70% (por ejemplo, en un rociador, 7 partes de alcohol con 3 partes de agua destilada o hervida)",
        "",
        "<b>Actuemos con solidaridad</b>, siendo <b>respetuosos</b> y <b>amables</b> con todos los demás.",
        "Tené en cuenta que <b>el objetivo es frenar el contacto con el virus</b>.",
        "",
        "▶️ Cuidarte es cuidarnos.",
        menu_principal + medidas
    ],
    # Medidas -> AislamientoSocial -> AislamientoSocialPerros
    "/AislamientoSocialPerros": [
        "Te acercamos una serie de recomendaciones importantes para cuidar la salud de tu mascota, la tuya y la de todos durante el período de aislamiento social, preventivo y obligatorio",
        "",
        " - Las mascotas pueden ser sacadas afuera (no a pasear) solo por una persona.",
        " - La distancia de recorrida durante el paseo debe ser la mínima posible, en las inmediaciones de la casa.",
        " - Se debe llevar lavandina para echar sobre la orina y sobre el lugar en el que se recogieron las heces del animal.",
        " - Durante el paseo se deben guardar las medidas de distanciamiento social y respetar las pautas de higiene recomendadas para las personas.",
        " - Al regresar, es necesario desinfectar las patas de las mascotas, con agua y jabón, y luego lavarse bien las manos y cambiarse la ropa.",
        " - Los paseos deben hacerse a la mañana temprano y a la noche.",
        menu_principal + medidas
    ],
    # Medidas -> AislamientoSocial -> AislamientoSocialServicios
    "/AislamientoSocialServicios": [
        "<b>Línea 144 de asistencia por violencia de género</b>",
        "El Ministerio de las Mujeres, Géneros y Diversidad desarrolló una aplicación gratuita que, de manera complementaria a la línea 144, brinda contención y asesoramiento ante situaciones de violencia de género.",
        "<a href='https://www.argentina.gob.ar/aplicaciones/linea-144-atencion-mujeres'>Descargá la aplicación</a>",
        "",
        "<b>Línea 141 de asistencia por consumos problemáticos y guía de recomendaciones</b>",
        "La SEDRONAR ofrece atención gratuita para asistir y responder consultas respecto de situaciones de consumo de sustancias las 24 horas a través de la línea 141, y recomendaciones para Comunidades Terapéuticas y Casas con Convivencia, y para aquellos que asisten a personas en situación de calle.",
        "<a href='https://www.argentina.gob.ar/sedronar/covid-19'>Leé la información de SEDRONAR</a>",
        "",
        "<b>Trámites a distancia</b>",
        "A través de la plataforma TAD podés realizar trámites ante organismos públicos nacionales desde tu casa. Aquellos que son pagos pueden abonarse en la misma plataforma.",
        "<a href='https://www.argentina.gob.ar/jefatura/innovacion-publica/administrativa/tramites-a-distancia'>Conocé como usar TAD</a>",
        "",
        "<b>Detalles del aislamiento en video</b>",
        "La Agencia Nacional de Discapacidad pone a disposición un video que incluye explicación en lenguaje de señas argentina.",
        "<a href='https://youtu.be/uZcFreMhODs'>Mirá el video</a>",
        "",
        "<b>Seguimos educando, un portal de recursos educativos en línea</b>",
        "Con el objetivo de colaborar con la continuidad de las actividades de enseñanza en el sistema educativo nacional, el Ministerio de Educación de la Nación ofrece actividades, videos, libros digitales, series y otros contenidos del portal educ.ar. Además, la <a href='https://www.tvpublica.com.ar/programa/seguimos-educando/'>Televisión Pública</a> emitirá 4 horas diarias de contenidos educativos de las señales <a href='http://encuentro.gob.ar/'>Encuentro</a> y <a href='http://encuentro.gob.ar/'>Pakapaka</a>.",
        "<a href='https://www.educ.ar/recursos/150936/seguimos-educando'>Conocé Seguimos Educando</a>",
        "",
        "<b>Plataforma de contenidos Contar</b>",
        "Además de sumarse a la iniciativa del Ministerio de Educación y ofrecer una selección de contenidos didácticos, esta plataforma reúne las propuestas del Sistema de Medios Públicos; TV Pública, Canal Encuentro, PakaPaka, DeportTV, espectáculos de Tecnópolis y CCK. El acceso al contenido es totalmente gratuito y está disponible tanto a través de la web como de aplicaciones para iOS y Android.",
        "<a href='https://www.cont.ar/'>Ingresá a Contar</a>",
        menu_principal + medidas
    ],
    # Medidas -> AislamientoSocial -> Decreto
    "/DNU2602020": [
        "El Presidente de la Nación firmó el 12 de marzo de 2020 el Decreto de Necesidad y Urgencia que amplía la Emergencia Sanitaria y dispone la adopción de nuevas medidas para contener la propagación del nuevo coronavirus.",
        "El decreto faculta al Ministerio de Salud, como autoridad de aplicación, a adquirir equipamiento, bienes y servicios, y a adoptar las medidas de salud pública necesarias.",
        "Protege a su vez los insumos críticos como el alcohol en gel o barbijos, suspende los vuelos provenientes de las zonas afectadas por el virus y dispone la obligatoriedad del aislamiento en los casos que en la normativa se detallan.",
        "En vistas de que el 11 de marzo de 2020 la Organización Mundial de la Salud (OMS) declaró el brote del nuevo coronavirus como una pandemia, el Gobierno nacional dispuso la adopción de nuevas medidas con el fin de mitigar su propagación e impacto sanitario.",
        "Entre las principales acciones y regulaciones, la normativa dispone:",
        "La ampliación de la Emergencia Sanitaria por el plazo de un año, facultando al Ministerio de Salud como autoridad de aplicación.",
        "Que el Ministerio de Salud brindará un informe diario respecto de las zonas afectadas por el virus y la situación epidemiológica.",
        "La protección de insumos críticos por parte del Ministerio de Salud de la Nación, en articulación con el Ministerio de Desarrollo Productivo.",
        "El establecimiento del aislamiento obligatorio por 14 días para las personas:",
        " - que revistan la condición de “casos sospechosos”: presencia de fiebre y uno o más síntomas respiratorios (tos, dolor de garganta o dificultad respiratoria) y que además tenga historial de viaje a las zonas afectadas o haya estado en contacto con casos confirmados o probables de COVID-19;",
        " - con confirmación médica de haber contraído COVID- 19;",
        " - contactos estrechos de los dos casos anteriores;",
        " - que arriben al país habiendo transitando por zonas afectadas;",
        " - que hayan arribado al país en los últimos 14 días, habiendo transitado por zonas afectadas por el nuevo coronavirus.",
        "La obligación de la población de reportar de forma inmediata síntomas compatibles a los del COVID-19 a los prestadores de salud bajo la modalidad que establezca cada jurisdicción.",
        "La suspensión de los vuelos internacionales de pasajeros provenientes de las zonas afectadas, durante el plazo de 30 días.",
        "La posibilidad de disponer el cierre de museos, centros deportivos, salas de juegos, restaurantes, piscinas y demás lugares de acceso público; suspender espectáculos públicos y todo otro evento masivo; imponer distancias de seguridad y otras medidas necesarias para evitar aglomeraciones.",
        "La sanción de las infracciones que se efectuaran respecto de las medidas previstas en el Decreto. Las mismas se aplicarán según la normativa vigente.",
        "La constitución de la “Unidad de Coordinación General del Plan Integral para la Prevención de Eventos de Salud Pública de Importancia Internacional”. La misma será coordinada por el Jefe de Gabinete de Ministros y estará integrada por las áreas pertinentes del Ministerio de Salud de la Nación y las demás jurisdicciones y entidades que tengan competencia en la materia.",
        "",
        "https://www.boletinoficial.gob.ar/suplementos/2020031201NS.pdf",
        menu_principal + medidas
    ],
    # Informe diario
    "/Informe": [
        "Informe oficial: https://www.argentina.gob.ar/coronavirus/informe-diario",
        "",
        "PHOTO|https://ibin.co/5Gjjw4pDXqeQ.png|Fuente del gráfico El Gato y la Caja",
        menu_principal
    ],
    # Preguntas frecuentes
    "/Preguntas": ["<b>Preguntas frecuentes sobre SARS-COV2 y enfermedad por coronavirus (COVID-19)</b>\n"] + faqs + [menu_principal],
    # Telefonos
    "/Telefonos": [
        "<b>Teléfonos y contactos útiles</b>",
        "",
        "☎️ <b>0800-222-1002</b>",
        "0800 Salud Responde, opción 1. Teléfono gratuito para llamados desde todo el país.",
        "",
        "📞 <b>134</b>",
        "Para denunciar a quienes violen la cuarentena, comunicate con el Ministerio de Seguridad al número gratuito 134.",
        "",
        "🌐 <b>Asistencia a los argentinos en el exterior</b>",
        "Podés escribir a estos correos electrónicos de la Cancillería argentina dependiendo del lugar donde te encuentres.",
        " - Europa: covideuropa@cancilleria.gob.ar",
        " - Estados Unidos y Canadá: covidnorte@cancilleria.gob.ar",
        " - América Central, Caribe y México: covidcentral@cancilleria.gob.ar",
        " - América del Sur: covidsur@cancilleria.gob.ar",
        " - Asia, Oceanía, Africa y Medio Oriente: covidrestmun@cancilleria.gob.ar",
        "",
        "📱 <b>Videollamada para personas sordas e hipoacúsicas</b>",
        "La Agencia Nacional de Discapacidad ofrece un servicio exclusivo para personas con discapacidad auditiva, el número 11-5728-4011, disponible de lunes a viernes de 10 a 15 horas.",
        "",
        "Para ver los teléfonos por jurisdicción visitar: https://www.argentina.gob.ar/coronavirus/telefonos",
        menu_principal
    ],
    "/Plan": [
        "https://www.argentina.gob.ar/salud/coronavirus-COVID-19/plan-operativo",
        menu_principal
    ],
    "/Salud": [
        "<b>Situación epidemiológica</b>",
        "El 31 de diciembre de 2019, China notificó la detección de casos confirmados por laboratorio de una nueva infección por coronavirus (COVID-19) que posteriormente fueron confirmados en varios países de distintos continentes. La evolución de este brote motivó la declaración de la OMS de una emergencia de salud pública de importancia internacional (ESPII).",
        "",
        "Para consultar información actualizada sobre número de casos detectados, fallecidos y la localización de los mismos, referirse a <a href='https://www.who.int/emergencies/diseases/novel-coronavirus-2019/situation-reports/'>Reportes de Situación OMS- sólo en inglés</a>.",
        "",
        "A la fecha, la Organización Mundial de la Salud continúa la investigación sobre el nuevo patógeno y el espectro de manifestaciones que pueda causar, la fuente de infección, el modo de transmisión, el periodo de incubación, la gravedad de la enfermedad y las medidas específicas de control.",
        "",
        "La evidencia actual sugiere que la propagación de persona a persona está ocurriendo, incluso entre los trabajadores de la salud que atienden a pacientes enfermos de COVID-19, lo que sería consistente con lo que se sabe sobre otros patógenos similares como el SARS y el coronavirus causante del MERS- CoV.",
        "",
        "<b>Declaración de la OMS</b>",
        "El 30 de enero de 2020, el Director General de la OMS declaró que el brote del nuevo coronavirus constituye una emergencia de salud pública de importancia internacional (ESPII) en el marco del Reglamento Sanitario Internacional.",
        "Con la consecuente emisión de recomendaciones tanto para el país donde se está produciendo el evento, como para el resto de los países y a la comunidad global. Donde se destacan que se espera que una mayor exportación internacional de casos pueda aparecer en cualquier país.",
        "todos los países deben estar preparados para la contención, incluida la vigilancia activa, la detección temprana, el aislamiento y el manejo de casos, el seguimiento de contactos y la prevención de la propagación de la infección por COVID-19, y compartir datos completos con la OMS.",
        "El 11 de marzo de 2020, el director general de la OMS declaró el estado de <a href='https://www.who.int/es/dg/speeches/detail/who-director-general-s-opening-remarks-at-the-media-briefing-on-covid-19---11-march-2020'>pandemia</a>.",
        "",
        "▶️ <a href='http://www.msal.gob.ar/index.php?filter_problematica=100&filter_soporte=0&palabra_clave=&option=com_bes_contenidos'>Materiales para equipos de salud</a>",
        menu_principal
    ],
    "/Autotest": [
        "https://www.argentina.gob.ar/coronavirus/app",
        menu_principal
    ],
    # Rumores OMS
    "/Rumores": ["<b>Consejos para la población acerca de los rumores sobre el nuevo coronavirus (2019-nCoV)</b> (Por la OMS, 13 de marzo de 2020)\n"] + oms_faqs + [menu_principal],
}

answers.update(faq_answers)

answers.update(oms_faq_answers)

# Configure Telegram connection
telegram_conection = telegram("CovidArBot", Config.telegram_token, "8979")
# chat_history = {}
while 1:
    telegram_conection.open_session()
    # telegram_conection.deleteWebhook()
    r = telegram_conection.get_update()  # Listen for new messages
    if not r:
        print("no messages")
        continue  # If no messages continue loop
    r_json = r.json()
    telegram_conection.close_session()
    for result in r_json["result"]:
        answer = ""
        # print(result)
        if not ("message" in result and "text" in result["message"]):
            continue  # Sanity check on the message

        chat_id = result["message"]["chat"]["id"]  # Get user id
        input_text = result["message"]["text"]  # Get input text

        print(input_text)
        msg_str = "\n".join(answers["/start"])
        photos = []
        if input_text in answers:
            msg_str = ""
            for line in answers[input_text]:
                if line.startswith("PHOTO|"):
                    photos.append(line.split("|"))
                else:
                    msg_str += line + "\n"
        print(msg_str)
        print()

        telegram_conection.sendMessage(chat_id, msg_str)
        for photo in photos:
            telegram_conection.sendPhoto(chat_id, photo[1], photo[2])
